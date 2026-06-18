# sources/user-network-fs/rclone/cmd/ls/lshelp/lshelp.go

Purpose: provides shared help text for list-family commands (`ls`, `lsl`, `lsd`, `lsf`, `lsjson`) to keep docs consistent.

Important API: exported `Help` string. The raw text uses `|` as a placeholder, then `strings.ReplaceAll` converts it to backticks for Markdown.

Control flow/state: no runtime behavior beyond package initialization. It documents recursion defaults, filtering applicability, ListR/fast-list behavior, and behavior on nonexistent directories.

Dependencies/integration: imported by command packages to append common help. Risks are documentation drift when list command behavior changes. There are no direct tests; generated docs or command help output indirectly exercise it.
