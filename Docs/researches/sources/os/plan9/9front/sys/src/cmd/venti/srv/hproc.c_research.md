# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/hproc.c

HTTP `/proc` debugger exposing process, thread, stack, symbol, segment, and file-descriptor views of the running Venti process.

Key behavior:
- Uses Plan 9 `/proc`, libmach, and libthread internals to open self text, map memory, resolve symbols, inspect registers, and walk stacks.
- Serves endpoints under `/proc/`: `all`, `segment`, `fd`, `procs`, `threads`, `stacks`, and `symbols`.
- `procapply` walks the libthread process queue `_threadpq`.
- `threadapply` maps each proc pid and walks its thread queue.
- `threadfmt` prints thread pointer, state, likely source line, moribund status, and command name.
- `stacktracepcsp`/`ptrace` print function calls, parameters, locals, and source lines.

Interactions:
- Registered by `httpd.c` for prefix `/proc/`.
- Depends on specific libthread internal structs and jump-buffer offsets.

Notable details:
- A single static 64 KiB output buffer is protected by `debug.lock`; concurrent requests report debugger busy.
- This is an introspection/admin endpoint and should not be exposed to untrusted clients.
