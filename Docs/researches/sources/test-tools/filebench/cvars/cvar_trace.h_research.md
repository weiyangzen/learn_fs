<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/cvars/cvar_trace.h -->
# `sources/test-tools/filebench/cvars/cvar_trace.h`

Purpose: Lightweight logging and optional debug tracing for CVAR modules.

Important APIs/macros: `cvar_log_error(fmt, ...)` always writes to stderr with a final period. Under `DEBUG`, `cvar_trace(fmt, ...)` logs file/line/function and `cvar_tracebuf` formats a byte buffer as hex. Without `DEBUG`, `cvar_trace` compiles away and `cvar_tracebuf` is a no-op.

Control flow: debug `cvar_tracebuf` allocates a string sized for `0x` plus two hex chars per byte, fills it nibble-by-nibble, prints it, and frees it.

State and persistence: no persistent state; debug buffer allocation is transient.

Dependencies and integration: includes `stdio.h` and `stdlib.h`; used by token and distribution sources.

Risks: debug `cvar_tracebuf` writes `sbuf[2*len + 2] = '\0'` after allocating `2 + 2*len + 1` bytes, an off-by-one write. Several modules use `cvar_trace` for error conditions, meaning diagnostics vanish in non-debug builds. Variadic macro syntax relies on GNU `##__VA_ARGS__`.

Test signals: compile with and without `DEBUG`; run `cvar_tracebuf` under ASAN/Valgrind to catch the terminator write.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/cvars/cvar_trace.h -->
