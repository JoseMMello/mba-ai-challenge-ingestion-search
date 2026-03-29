from search import search_prompt


def main():
    chain = search_prompt()

    if not chain:
        print("Não foi possível iniciar o chat. Verifique os erros de inicialização.")
        return

    print("=" * 50)
    print("Chat RAG iniciado! Digite 'sair' para encerrar.")
    print("=" * 50)

    while True:
        pergunta = input("\nVocê: ").strip()

        if pergunta.lower() in ["sair", "exit", "quit"]:
            print("Até logo!")
            break

        if not pergunta:
            continue

        print("\nAssistente: ", end="", flush=True)

        resposta = chain(pergunta)
        print(resposta)


if __name__ == "__main__":
    main()