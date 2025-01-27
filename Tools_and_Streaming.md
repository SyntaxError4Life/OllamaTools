### **Approaches Tested for Multi-Tool Usage with Ollama (with Streaming)**

---

#### **1. Streaming with Integrated Tools**
- **Objective**: Use streaming to generate text and tool calls in the same stream, hoping the model alternates between text and tools.
- **Findings**:
  - Ollama generates tool calls **from the first chunk**, without the possibility of generating text beforehand.
  - Text chunks (`content`) and tool chunks (`tool_calls`) are **mutually exclusive**: a chunk cannot contain both.
  - The model does not follow instructions to generate text before calling a tool.
- **Example Request**:
  ```python
  stream = chat(
      model="mistral",
      messages=[{"role": "user", "content": "What's the weather like in Paris?"}],
      tools=tools,
      stream=True
  )
  ```
  **Result**: The model immediately calls the `get_weather` tool without generating any preliminary text.
  **Conclusion**: The server forces all function calls at the beginning.

---

#### **2. Two-Phase Workflow**
- **Objective**: Split the conversation into two phases:  
  1. Text generation without tools.  
  2. Tool calls with confirmation.
- **Findings**:
  - Phase 1 works: the model generates text without using tools.
  - Phase 2 often fails: the model does not call a tool even with an explicit system prompt.
  - The model does not always understand the need to use a tool after generating text.
- **Example Request**:
  ```python
  # Phase 1
  response_text = chat(
      model="mistral",
      messages=[{"role": "system", "content": "Respond without using tools."}],
      stream=False
  )
  
  # Phase 2
  response_tool = chat(
      model="mistral",
      messages=[{"role": "system", "content": "Use a tool if necessary."}],
      tools=tools,
      stream=False
  )
  ```
  **Result**: The model generates text in phase 1 but does not call a tool in phase 2.
  **Conclusion**: I believe the issue lies with the model, but it's not exploitable in all cases.

---

#### **3. Custom Tags**
- **Objective**: Force the model to use a custom tag format for tools (e.g., `[tool]...[/tool]`), then intercept and execute the tools manually.
- **Procedure**: 
   - I created a module that reads the content of streaming chunks and adds a latency of 3 tokens (the size of [tool]).
   - Once the tool is executed, I provide the model with the response and let it complete the text, concatenating everything at the end.
- **Findings**:
  - The model does not always respect the tag format, even with a strict system prompt.
  - Tags are often malformed or incomplete, making interception difficult.
  - The added latency to intercept tags does not solve the underlying issue.
- **Example Request**:
  ```python
  stream = chat(
      model="mistral",
      messages=[{"role": "system", "content": "Use [tool]...[/tool] for tools."}],
      stream=True
  )
  ```
  **Result**: The model often ignores the tags or generates malformed tags.
  **Conclusion**: 

---

#### **4. Multi-Call with Shared Context**
- **Objective**: Use multiple separate calls to generate text, then call tools, and finally generate a final response.
- **Findings**:
  - This approach works partially, but it is **cumbersome** and requires manual context management.
  - The model does not always understand how to use the results of the tools in the final response.
  - Performance is degraded due to the multiple calls required.
- **Example Request**:
  ```python
  # Call 1: Text generation
  response_text = chat(
      model="mistral",
      messages=[{"role": "user", "content": "What's the weather like in Paris?"}],
      stream=False
  )
  
  # Call 2: Tool call
  response_tool = chat(
      model="mistral",
      messages=[{"role": "user", "content": "Do you want to call a tool or stop?"}],
      tools=tools,
      stream=False
  )
  ```
  **Result**: The model generates text in the first call, but the tool call in the second call is often ignored.
  **Conclusion**: The method is sound, but the issue lies with the model, which is not designed for this.

---

#### **5. Client-Server Hybrid Approach**
- **Objective**: Use an external client to manage tool calls and text responses, similar to the OpenAI API.
- **Findings**:
  - The problem lies with the **Ollama server**, which does not allow modifying the streaming flow after generation.
  - Ollama models are not designed to alternate between text and tools in a single stream.
  - This approach does not resolve Ollama's intrinsic limitations.
- **Example Request**:
  ```python
  stream = chat(
      model="mistral",
      messages=[{"role": "user", "content": "What's the weather like in Paris?"}],
      tools=tools,
      stream=True
  )
  ```
  **Result**: The model immediately calls the tool without generating any preliminary text.

---

### **Conclusion**
All tested approaches failed to allow seamless use of tools **at any point** in the conversation. The main limitations are:
1. **Ollama Server**: Streaming chunks do not allow mixing text and tool calls.
2. **Models**: Models (Mistral, Llama3.1, and 3.2) prioritize tools as soon as the request matches their description, without generating preliminary text.
3. **Architecture**: Ollama is not designed to handle complex workflows with alternation between text and tools.

To solve these issues, it would be necessary to **modify the Ollama server** to:
- Allow mixed chunks (text + tools).
- Implement a priority logic to force the model to generate text before calling a tool.
- Add finer management of tools in the streaming flow.

Without these modifications, it is difficult to effectively use tools with Ollama in a fluid conversational context.

---
---

### **Next Steps** 
I will work on a **custom client** using **transformers** directly and compile the models to allow optimization similar to Ollama.
