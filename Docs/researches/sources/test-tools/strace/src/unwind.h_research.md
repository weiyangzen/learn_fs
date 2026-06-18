<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/unwind.h -->
# sources/test-tools/strace/src/unwind.h

Purpose: Backend interface contract for stack unwinding, defining callback signatures and the `struct unwind_unwinder_t` vtable implemented by libdwfl/libunwind backends.

Important APIs/types/functions:
- Direct includes: `"defs.h"`
- Local/exported macros: `STRACE_UNWIND_H`

Control flow:
- control flow is linear around a small decoder/helper surface and returns standard strace `RVAL_*` flags

State and persistence behavior:
- no persistent storage; behavior is derived from current tracee arguments, return value, and build-time headers

Dependencies and integration points:
- depends on strace `defs.h` formatting/fetch APIs and listed kernel/libc headers
- requires libunwind-ptrace support and mmap cache integration

Risks:
- length/count fields need bounds-aware printing to avoid misleading output or excessive tracee reads

Test signals:
- compile coverage plus targeted decoder-output fixtures are the primary validation signal
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/unwind.h -->
