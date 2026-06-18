# File Research: sources/local-fs/jfsutils/libfs/debug.h

Simple conditional debug macro header.

Key contents:
- Includes `stdio.h`.
- Defines:
  - `DBG_TRACE(a)` enabled by `TRACE`, printing to stdout and flushing stdout.
  - `DBG_IO(a)` enabled by `TRACE_IO`, printing via `printf` and flushing stderr.
  - `DBG_ERROR(a)` enabled by `TRACE_ERROR`, printing to stdout and flushing stdout.
- When flags are absent, macros expand to empty statements.

Interactions:
- Used by `devices.c` and likely other libfs modules for optional diagnostics.

Research notes:
- `DBG_IO` flushes stderr after `printf` to stdout, which is inconsistent but harmless for compile-time disabled default.
