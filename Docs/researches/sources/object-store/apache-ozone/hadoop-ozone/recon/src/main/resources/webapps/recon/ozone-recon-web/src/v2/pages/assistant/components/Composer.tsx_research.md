# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/assistant/components/Composer.tsx

Purpose: Input composer for Recon AI, including provider/model picker, textarea, send-on-enter, and stop button.

Important APIs, types, and functions: Exports default `Composer`. Props include send/cancel callbacks, in-flight flag, models, controlled current query, and setter.

Control flow: Tracks selected provider/model locally. Provider changes reset model. Enter without Shift sends; Shift+Enter inserts a newline. In-flight state disables input/model picker and swaps send for stop.

State and persistence behavior: Local selected provider/model. Query text is controlled by the parent/useChat.

Dependencies: Uses AntD `Input.TextArea` and `Button`, send/stop icons, and `ModelPicker`.

Integration points: Rendered by Assistant and calls `useChat.sendMessage`/`cancelRequest` through props.

Risks and edge cases: Selected provider/model are not persisted between chats. Sending does not clear `currentQuery` immediately; `useChat` clears it after success only. Keyboard handling may surprise IME composition users.

Test signals: Cover disabled in-flight state, provider reset clearing model, Enter versus Shift+Enter, empty-query disabled send, stop callback, and selected model/provider passed to `onSend`.
