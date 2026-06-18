# File Research: sources/os/plan9/plan9/sys/src/cmd/acme/exec.c

This file implements tag command execution and external command launching.

Key behavior:
- `exectab` maps built-in commands: `Cut`, `Del`, `Dump`, `Edit`, `Exit`, `Font`, `Get`, `Kill`, `Look`, `New`, `Paste`, `Put`, `Redo`, `Send`, `Snarf`, `Sort`, `Tab`, `Undo`, `Zerox`, and more.
- `execute()` expands clicked text, sends events to external clients if needed, runs built-ins, or launches external commands.
- Built-ins implement window/column creation/deletion, file get/put, dump/load, cut/paste/snarf, search, edit, font selection, include path management, indentation, tabstop, kill, and command send.
- `putfile()` writes file ranges with qid/mtime/dev conflict checks and append-only rejection.
- `runproc()` creates the child namespace, mounts `/mnt/acme`, sets `%`, `winid`, `acmeaddr`, wires stdin/stdout/stderr for pipes, tries direct exec, then falls back to `rc -c`.
- `run()` starts command execution and a wait task without blocking Acme’s 9P mount path.

Important details:
- External command execution uses per-command `Mntdir` state and exposes Acme through `/mnt/acme` and `/dev`.
- `Cut`/`Paste` coordinate with undo sequence numbers and snarf buffer.
- `Putall` skips scratch, directories, nameless files, and windows with external event clients.
- `Get` refuses unsafe reloads and handles directory windows specially.
- Direct exec path rejects shell-special characters; complex commands run under `rc`.

Filesystem relevance:
- Very high: real file I/O, Acme pseudo-files, namespace construction, `/dev`, `/mnt/wsys`, plumber notifications, and safe-write semantics.
