import { useMemo, useRef, useState } from 'react';

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

function parseSSEChunk(rawChunk) {
  const line = rawChunk.split('\n').find((value) => value.startsWith('data:'));

  if (!line) return null;

  const payload = line.slice(5).trim();
  if (payload === '[DONE]') return { done: true };

  try {
    return JSON.parse(payload);
  } catch {
    return null;
  }
}

export default function App() {
  const [messages, setMessages] = useState([]);
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const readerRef = useRef(null);
  const requestSeqRef = useRef(0);

  const canSend = useMemo(() => question.trim().length > 0, [question]);

  async function ask(event) {
    event.preventDefault();
    if (!canSend) return;

    if (readerRef.current) {
      await readerRef.current.cancel();
      readerRef.current = null;
    }

    const requestId = ++requestSeqRef.current;
    const userMessage = question.trim();
    setQuestion('');
    setLoading(true);

    const nextMessages = [
      ...messages,
      { role: 'user', content: userMessage },
      { role: 'assistant', content: '' },
    ];
    setMessages(nextMessages);

    try {
      const response = await fetch(`${API_URL}/chat/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMessage }),
      });

      if (!response.ok || !response.body) {
        throw new Error('Falha ao iniciar streaming da resposta.');
      }

      const reader = response.body.getReader();
      readerRef.current = reader;

      const decoder = new TextDecoder('utf-8');
      let buffer = '';
      let answer = '';

      while (true) {
        if (requestId !== requestSeqRef.current) break;
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const chunks = buffer.split('\n\n');
        buffer = chunks.pop() ?? '';
        for (const rawChunk of chunks) {
          const parsed = parseSSEChunk(rawChunk);
          if (!parsed) continue;
          if (parsed.done) break;
          if (parsed.token) {
            answer += parsed.token;
            setMessages((current) => {
              const updated = [...current];
              updated[updated.length - 1] = {
                role: 'assistant',
                content: answer,
              };
              return updated;
            });
          }
        }
      }
    } catch (error) {
      if (requestId === requestSeqRef.current) {
        const msg = error instanceof Error ? error.message : 'Erro inesperado.';
        setMessages((current) => [
          ...current,
          {
            role: 'assistant',
            content: `Erro ao responder: ${msg}`,
          },
        ]);
      }
    } finally {
      if (requestId === requestSeqRef.current) {
        setLoading(false);
        readerRef.current = null;
      }
    }
  }

  function stopStreaming() {
    readerRef.current?.cancel();
    readerRef.current = null;
    setLoading(false);
  }

  return (
    <main className="layout">
      <section className="chat-card">
        <header className="chat-header">
          <h1>RAG Chat</h1>
          <p>Pergunte sobre o conteúdo indexado e veja a resposta em stream.</p>
        </header>

        <div className="messages">
          {messages.length === 0 ? (
            <p className="empty">Comece com uma pergunta para o assistente.</p>
          ) : (
            messages.map((message, index) => (
              <article
                key={`${message.role}-${index}`}
                className={`message ${message.role}`}
              >
                <strong>
                  {message.role === 'user' ? 'Você' : 'Assistente'}
                </strong>
                <p>
                  {message.content ||
                    (loading && message.role === 'assistant' ? '...' : '')}
                </p>
              </article>
            ))
          )}
        </div>

        <form className="composer" onSubmit={ask}>
          <input
            type="text"
            placeholder="Digite sua pergunta"
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
          />
          <button type="submit" disabled={!canSend}>
            Enviar
          </button>
          {loading && (
            <button type="button" className="ghost" onClick={stopStreaming}>
              Parar
            </button>
          )}
        </form>
      </section>
    </main>
  );
}
