from rest_framework import serializers
from .models import Task, Category, ContextEntry

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ContextEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = ContextEntry
        fields = '__all__'

class TaskSerializer(serializers.ModelSerializer):
    # ✅ Nested serializer for reading category details
    category = CategorySerializer(read_only=True)
    
    # ✅ Allow writing category via ID
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True,
        required=False  # Optional if some tasks don’t have category
    )

    class Meta:
        model = Task
        # Explicitly include category_id for POSTs
        fields = [
            'id',
            'title',
            'description',
            'priority_score',
            'deadline',
            'category',      
            'category_id',  
            'created_at',
            'updated_at'
        ]