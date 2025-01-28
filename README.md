# Documentation: Using Tools with Ollama

This documentation explains how to use function calls (tools) with Ollama, based on models like Llama3.1 and Mistral. It describes the format of messages, tools, and responses.

---

## **1. Tool Structure**

A tool is a function that the model can call to obtain information or perform actions. Here is the JSON format of a tool:

```json
{
    "type": "function",
    "function": {
        "name": "function_name",
        "description": "Description of what the function does",
        "parameters": {
            "type": "object",
            "properties": {
                "param1": {"type": "string", "description": "Description of the parameter"},
                "param2": {"type": "number", "description": "Description of the parameter"}
            },
            "required": ["param1"]  // Required parameters
        }
    }
}
```

### Example for a `get_current_time` function:
```json
{
    "type": "function",
    "function": {
        "name": "get_current_time",
        "description": "Get the current time",
        "parameters": {"type": "object", "properties": {}}
    }
}
```

---

## **2. Message Format**

Messages are structured in JSON and must follow a specific order to handle function calls.

### Available roles:
- **`system`**: Global instructions for the model.
- **`user`**: User message.
- **`assistant`**: Model response **OR** function call.
- **`tool`**: Tool response after execution.

---

### **2.1. Function Call by the Model**

When the model decides to call a function, it returns a message with the `assistant` role and a `tool_calls` field:

```json
{
    "role": "assistant",
    "content": "",  // Empty during a function call
    "tool_calls": [
        {
            "function": {
                "name": "function_name",
                "arguments": "{}"  // Arguments in JSON format
            }
        }
    ]
}
```

#### Example:
```json
{
    "role": "assistant",
    "content": "",
    "tool_calls": [
        {
            "function": {
                "name": "get_current_time",
                "arguments": "{}"
            }
        }
    ]
}
```

---

### **2.2. Tool Response**

After executing the function, you must add a message with the `tool` role to provide the result to the model:

```json
{
    "role": "tool",
    "name": "function_name",
    "content": "Function result"
}
```

#### Example:
```json
{
    "role": "tool",
    "name": "get_current_time",
    "content": "15:30:45"
}
```

---

### **2.3. Final Model Response**

The model uses the tool result to generate a final response:

```json
{
    "role": "assistant",
    "content": "Final response based on the tool result"
}
```

#### Example:
```json
{
    "role": "assistant",
    "content": "It is currently 15 hours, 30 minutes, and 45 seconds."
}
```

---

## **3. Complete Conversation Flow**

Here is an example of a complete flow for requesting the current time:

### **Step 1: User Message**
```json
{
    "role": "user",
    "content": "What time is it?"
}
```

### **Step 2: Function Call by the Model**
```json
{
    "role": "assistant",
    "content": "",
    "tool_calls": [
        {
            "function": {
                "name": "get_current_time",
                "arguments": "{}"
            }
        }
    ]
}
```

### **Step 3: Tool Response**
```json
{
    "role": "tool",
    "name": "get_current_time",
    "content": "15:30:45"
}
```

### **Step 4: Final Model Response**
```json
{
    "role": "assistant",
    "content": "It is currently 15 hours, 30 minutes, and 45 seconds."
}
```

---

## **4. Python Code Example**

Here is an example of a complete program to handle a conversation with a function call:

```python
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
    model="llama3.1", # Works with mistra (and is better)
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
    final_response = chat(
        model="llama3.1",
        messages=messages
    )
    print("Final response:", final_response.message.content)
else:
    print("No function call detected.")
```

---

## **5. Best Practices**

1. **Clear Instructions**: Use a `system` message to guide the model.
2. **Argument Validation**: Always validate arguments before executing a function.
3. **Error Handling**: Add checks for cases where the model does not call a function.
4. **Response Format**: Ensure tool responses are well-structured.

---
---

## **Repository Evolution**

This repository is constantly evolving.

- **Additional Examples**: Adding practical cases with more complex tools.
- **Advanced Workflows**: Examples of nested workflows with multiple tool calls.
- **Integrations**: Examples of integration with other libraries or services (e.g., external APIs).

## **License**
This repository is public documentation. You are free to use it as you see fit.
