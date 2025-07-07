from openai import OpenAI

client = OpenAI(api_key='API KEY')  # replace with env var if needed

def generate_task_insights(task, context):
    prompt = f"""
    Task: {task}
    Context: {context}
    Generate:
    - Priority score (1-10)
    - Suggested deadline
    - Improved description
    - Suggested category/tag
    """
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    return response.choices[0].message.content