from openai import OpenAI
from dotenv import load_dotenv
from pydantic import BaseModel
import os
import json
from tools import TOOL_SCHEMAS, AVAILABLE_TOOLS
from llm.factory import build_client, select_provider

load_dotenv()

def ask_llm_with_tool(prompt: str) -> str: 
    """ call the LLM with tools """
    provider = select_provider()
    client = build_client(provider)
    messages = [
        {"role": "system", "content": "You are a helpful assistant. Use tools when necessary."},
        {"role": "user", "content": prompt}
    ]
    response = client.chat.completions.create(
        model = os.getenv(provider.model),
        messages = messages,
        tools = TOOL_SCHEMAS
    )


    if response.choices[0].message.tool_calls:
        messages.append(response.choices[0].message)
        response_message = response.choices[0].message.tool_calls
        for tool_call in response_message:
            function_name = tool_call.function.name

            if function_name in AVAILABLE_TOOLS:
                print(f"executing tool: {function_name}...")
                function_args = json.loads(tool_call.function.arguments)
                function_to_call = AVAILABLE_TOOLS[function_name]
                function_response = function_to_call(**function_args)

                messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": str(function_response)
                })

        print("Synthesizing final response...")
        second_response = client.chat.completions.create(
            model= os.getenv(provider.model),
            messages= messages
        )
        return second_response.choices[0].message.content
    
    else:
        return response.choices[0].message.content

    
QUESTION = "What is the weather of Jamshedpur compared to Ranchi?".strip()
print(ask_llm_with_tool(QUESTION))
    