import os
from typing import Callable, Generator, Optional
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_postgres import PGVector

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
COLLECTION_NAME = os.getenv("PG_VECTOR_COLLECTION_NAME", "documents")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
OPENAI_CHAT_MODEL = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")

PROMPT_TEMPLATE = """
CONTEXTO:
{contexto}

REGRAS:
- Responda somente com base no CONTEXTO.
- Se a informação não estiver explicitamente no CONTEXTO, responda:
  "Não tenho informações necessárias para responder sua pergunta."
- Nunca invente ou use conhecimento externo.
- Nunca produza opiniões ou interpretações além do que está escrito.

EXEMPLOS DE PERGUNTAS FORA DO CONTEXTO:
Pergunta: "Qual é a capital da França?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Quantos clientes temos em 2024?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Você acha isso bom ou ruim?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

PERGUNTA DO USUÁRIO:
{pergunta}

RESPONDA A "PERGUNTA DO USUÁRIO"
"""

template = PromptTemplate(
    template=PROMPT_TEMPLATE,
    input_variables=["contexto", "pergunta"],
)


def _build_components() -> tuple:
    embeddings = OpenAIEmbeddings(
        model=OPENAI_EMBEDDING_MODEL,
        api_key=OPENAI_API_KEY,
    )

    vectorstore = PGVector(
        connection=DATABASE_URL,
        collection_name=COLLECTION_NAME,
        embeddings=embeddings,
    )

    retriever = vectorstore.as_retriever(search_kwargs={"k": 10})

    llm = ChatOpenAI(
        model=OPENAI_CHAT_MODEL,
        api_key=OPENAI_API_KEY,
        temperature=0,
    )

    return retriever, llm


def _build_prompt(retriever, pergunta: str) -> str:
    docs = retriever.invoke(pergunta)
    contexto = "\n\n---\n\n".join([doc.page_content for doc in docs])
    return template.format(contexto=contexto, pergunta=pergunta)


def search_prompt() -> Optional[Callable[[str], str]]:
    try:
        retriever, llm = _build_components()

        def chain(pergunta: str) -> str:
            prompt = _build_prompt(retriever, pergunta)
            resposta = llm.invoke(prompt)
            return resposta.content

        return chain
    except Exception as e:
        print(f"Erro ao inicializar a busca: {e}")
        return None


def search_prompt_stream() -> Optional[Callable[[str], Generator[str, None, None]]]:
    try:
        retriever, llm = _build_components()

        def chain_stream(pergunta: str) -> Generator[str, None, None]:
            prompt = _build_prompt(retriever, pergunta)
            for chunk in llm.stream(prompt):
                if chunk.content:
                    yield chunk.content

        return chain_stream
    except Exception as e:
        print(f"Erro ao inicializar a busca em streaming: {e}")
        return None
