import re
from datetime import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Task, Category, ContextEntry
from .serializers import TaskSerializer, CategorySerializer, ContextEntrySerializer
from .ai_utils import generate_task_insights

# --- ✅ AI Insight Parser ---
def parse_insights(raw):
    lines = raw.splitlines()
    data = {}
    for line in lines:
        if line.lower().startswith("priority"):
            match = re.search(r"\d+", line)
            if match:
                data["priority_score"] = int(match.group())
        elif line.lower().startswith("deadline"):
            date_str = line.split(":", 1)[-1].strip()
            try:
                data["deadline"] = datetime.strptime(date_str, "%Y-%m-%d")
            except:
                data["deadline"] = None
        elif line.lower().startswith("description"):
            data["description"] = line.split(":", 1)[-1].strip()
        elif line.lower().startswith("category"):
            data["category"] = line.split(":", 1)[-1].strip()
    return data

# --- ✅ Views ---

class TaskList(APIView):
    def get(self, request):
        tasks = Task.objects.all().order_by('-priority_score')
        return Response(TaskSerializer(tasks, many=True).data)

    def post(self, request):
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            task = serializer.save()

            # ✅ Update category usage count if category exists
            if task.category:
                task.category.usage_count += 1
                task.category.save()

            return Response(TaskSerializer(task).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CategoryList(APIView):
    def get(self, request):
        categories = Category.objects.all()
        return Response(CategorySerializer(categories, many=True).data)

class ContextEntryList(APIView):
    def get(self, request):
        entries = ContextEntry.objects.all().order_by('-timestamp')
        return Response(ContextEntrySerializer(entries, many=True).data)

    def post(self, request):
        serializer = ContextEntrySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AISuggestions(APIView):
    def post(self, request):
        try:
            task = request.data.get("task")
            context = request.data.get("context")
            raw_result = generate_task_insights(task, context)

            insights = parse_insights(raw_result)

            # ✅ Create or get category
            category_obj = None
            if insights.get("category"):
                category_obj, _ = Category.objects.get_or_create(name=insights["category"])

            return Response({
                "suggestion": raw_result,
                "priority_score": insights.get("priority_score"),
                "deadline": insights.get("deadline"),
                "improved_description": insights.get("description"),
                "category_id": category_obj.id if category_obj else None,
                "category_name": category_obj.name if category_obj else None
            })

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)