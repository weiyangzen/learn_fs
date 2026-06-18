# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/hooks/useChat.hook.tsx

Purpose: Manages Recon AI chat message state, in-flight request lifecycle, elapsed timer, cancellation, persistence, and user-facing error normalization.

Important APIs, types, and functions: Exports `useChat` returning messages, in-flight state, elapsed seconds, error bubble, current query, `sendMessage`, `cancelRequest`, `clearMessages`, and `setCurrentQuery`.

Control flow: Loads messages from `sessionStorage`, appends a user message unless it duplicates the last user message, builds a chat request with optional provider/model, posts via `AxiosPostHelper`, appends assistant response, and maps HTTP 400/500/503/504 errors to display text. Abort cancels the request and timer.

State and persistence behavior: Persists `messages` under `recon_ai_messages`; local state tracks in-flight, elapsed seconds, error bubble, and current query. Refs hold abort controller, timer, and in-flight guard.

Dependencies: Uses `AxiosPostHelper`, Axios error helpers, chatbot types/constants, React hooks, and `crypto.randomUUID`.

Integration points: Consumed by `pages/assistant/assistant.tsx` and its Composer/MessageList components.

Risks and edge cases: Session storage JSON parse failures only log. Duplicate suppression can skip intentional repeated prompts after navigation. Error mapping depends on backend text and provider/model selection. `crypto.randomUUID` requires modern browser support.

Test signals: Cover persistence load/save/clear, duplicate user-message behavior, cancel path, timer cleanup, provider/model request body, status-specific error bubbles, masked LLM errors, and retry/regenerate flows.
