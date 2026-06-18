## sources/object-store/minio-mc/cmd/update-notifier.go

Purpose: formats the user-facing "new mc version available" notice used by update checks. Important functions are `prepareUpdateMessage` and `colorizeUpdateMessage`.

Control flow returns no message if no download URL or non-positive age is supplied; otherwise it converts the age to a human-readable relative duration and renders either a boxed terminal notice or a two-line fallback when the terminal is too narrow. State is none beyond terminal width probing. Dependencies include `go-humanize`, `pb.GetTerminalWidth`, runtime OS checks, and color functions from `update-main.go`. Integration is through `getUpdateInfo`. Risks include Unicode box rendering on non-Windows terminals, ANSI-length calculations, and width fallback behavior. There are no direct tests in the subset; validation is mostly visual and terminal-dependent.
