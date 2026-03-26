import asyncio
from orchestrator import build_graph
from src.utils.constants import MESSAGES

async def async_main():
    graph = build_graph()
    print(MESSAGES["WELCOME"])

    while True:
        question = input(MESSAGES["PROMPT"]).strip()
        if question.lower() == "exit":
            break
        if not question:
            continue
        print()
        
        try:
            result = await graph.ainvoke({
                "question": question,
                "entities": [],
                "graph_facts": [],
                "answer": ""
            })
            print(MESSAGES["ANSWER"].format(answer=result['answer']))
        except Exception as e:
            print(f"Error during execution: {e}")
            print(MESSAGES["ERROR_MSG"])
            
        print(MESSAGES["DIVIDER"])

def main():
    asyncio.run(async_main())

if __name__ == "__main__":
    main()