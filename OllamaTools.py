from ollama import chat
import datetime

# Tool definition
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "Get the current time",
            "parameters": {"type": "object", "properties": {}}
        }
    }
]

# Initial conversation
messages = [
    {"role": "system", "content": "Use tools when asked for the time."},
    {"role": "user", "content": "What time is it?"}
]

# Initial call
response = chat(
    model="llama3.1",
    messages=messages,
    tools=tools
)

def get_current_time():
    return datetime.datetime.now().strftime("%H:%M:%S")

# If a function call is detected
if hasattr(response.message, 'tool_calls') and response.message.tool_calls:
    # Add the assistant's response to the context
    messages.append({"role": "assistant", "content": "", "tool_calls": response.message.tool_calls})
    
    # Fictional tool response
    tool_response = {
        "role": "tool",
        "name": "get_current_time",
        "content": f"{get_current_time()}"
    }
    messages.append(tool_response)
    
    # Final response
    response2 = chat(
        model="llama3.1",
        messages=messages,
        stream=True
    )
    final_response = ""

    print("Final response: ", end="")
    for chunk in response2 :
        a = chunk.message.content
        print(a, end="")
        final_response += a
    print()
else:
    print("No function call detected.")