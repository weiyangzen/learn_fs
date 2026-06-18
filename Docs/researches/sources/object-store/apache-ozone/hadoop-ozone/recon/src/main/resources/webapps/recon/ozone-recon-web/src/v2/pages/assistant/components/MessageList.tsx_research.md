# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/assistant/components/MessageList.tsx

Purpose: Scrollable chat transcript with auto-scroll, loading bubble, and retryable error bubble.

Important APIs, types, and functions: Exports `MessageList` with messages, in-flight state, elapsed seconds, error bubble, retry callback, and regenerate callback.

Control flow: Maps messages to `MessageBubble`, auto-scrolls to a bottom ref whenever messages/loading/error change, adds `LoadingIndicator` during in-flight requests, and renders an assistant-styled error bubble with Retry button.

State and persistence behavior: Uses only a bottom DOM ref; no persisted state.

Dependencies: Uses AntD Button, `MessageBubble`, `LoadingIndicator`, `ReconAIMark`, and chatbot types.

Integration points: Used by Assistant when messages exist.

Risks and edge cases: Error icon is a Unicode symbol, unlike the icon library. Auto-scroll always uses smooth behavior, which can fight manual scrollback. Error bubble is not part of persisted message history.

Test signals: Cover auto-scroll trigger, regenerate index wiring, retry button, loading indicator, error bubble text, and empty/nonempty messages.
