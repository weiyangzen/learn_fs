# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/assistant/components/MessageBubble.tsx

Purpose: Renders one user or assistant chat message, including markdown, copy, and regenerate controls for assistant messages.

Important APIs, types, and functions: Exports `MessageBubble` with `message` and optional `onRegenerate`.

Control flow: User messages render plain text with user icon. Assistant messages render `ReactMarkdown` with GFM, show copy button using `copyToClipboard`, transient copied/copy-failed tooltip states, and optional regenerate button.

State and persistence behavior: Local `copied` and `copyFailed` booleans reset after two seconds.

Dependencies: Uses AntD Button/Tooltip/icons, `react-markdown`, `remark-gfm`, `classNames`, clipboard utility, and `ReconAIMark`.

Integration points: Used by `MessageList` for all persisted chat messages.

Risks and edge cases: Markdown rendering may allow unexpected link behavior unless markdown sanitization is handled by defaults. Copy timers are not cleared on unmount. User text is not markdown-rendered by design.

Test signals: Cover user/assistant rendering, markdown tables/lists, copy success/failure, timer reset, regenerate callback, and no actions for user messages.
