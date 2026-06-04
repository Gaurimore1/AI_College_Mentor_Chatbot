from rag_engine import get_rag_response

print("AI College Mentor Chatbot (RAG + LLaMA 3)")
print("Type 'quit' to exit.\n")

while True:
    query = input("Ask your mentor: ")

    if query.lower() == "quit":
        print("Good luck with your studies!")
        break

    try:
        answer = get_rag_response(query)
        print("\nMentor:", answer, "\n")
    except Exception as e:
        print("Error:", e)
