from openai import OpenAI
from dotenv import load_dotenv
from pydantic import BaseModel
import os
import json
from tools import TOOL_SCHEMAS, AVAILABLE_TOOLS
from llm.factory import build_client, select_provider
from llm.prompt_manager import PromptManager

load_dotenv()

def ask_llm_with_tool(messages: list, max_turns:int = 10) -> str: 
    """ call the LLM with tools """
    provider = select_provider()
    client = build_client(provider)
    prompt_manager = PromptManager()
    system_instruction =prompt_manager.build_system_prompt(tools_list=TOOL_SCHEMAS)
    working_messages= [
        {"role": "system", "content": system_instruction},
        *messages
    ]

    for turn in range(max_turns):

        response = client.chat.completions.create(
            model = os.getenv(provider.model),
            messages = working_messages,
            tools = TOOL_SCHEMAS
        )

        assistant_message = response.choices[0].message

        if assistant_message.tool_calls:
            working_messages.append(assistant_message)

            for tool_call in assistant_message.tool_calls:
                function_name = tool_call.function.name

                if function_name in AVAILABLE_TOOLS:
                    print(f"Executing tool: {function_name}...\n")
                    function_args = json.loads(tool_call.function.arguments)
                    function_to_call = AVAILABLE_TOOLS[function_name]
                    function_response = function_to_call(**function_args)

                    working_messages.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": str(function_response)
                    })
                
            continue
        
        else:
            return assistant_message.content
        
    return f"error: The agent reached maximium turns without completing the task"


if __name__ == "__main__":
    mananger = PromptManager()
    greeting = mananger.build_greeting()
    print(f"Agent: {greeting}\nType 'exit' or 'quit' to stop.")
    chat_history= []

    while True:
        user_input = input("\nYou: ").strip()

        if user_input.lower() in ["exit", "bye", "quit"]:
            print("\nAgent: Bye!")
            break

        if not user_input:
            continue
        
        chat_history.append(
            {
                "role": "user",
                "content": user_input
            }
        )
        response = ask_llm_with_tool(messages=chat_history)
        chat_history.append(
            {
                "role": "assistant",
                "content": response
            }
        )
        print(f"Agent: {response}")
    