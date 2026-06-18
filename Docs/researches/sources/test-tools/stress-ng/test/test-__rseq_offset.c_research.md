# sources/test-tools/stress-ng/test/test-__rseq_offset.c

Purpose: compile probe for restartable-sequence offset support, checking whether the toolchain and system headers expose `__rseq_offset` or compatible symbols used by stress-ng rseq helpers.

Important APIs/types/functions: rseq offset symbol access; observed symbols: `main` only with compile-time expressions; includes: `<stddef.h>`; macros: none.

Control flow: `main` references the rseq offset symbol and returns a simple value. The code is intentionally small so missing TLS/libc exposure fails at compile or link time.

State and persistence behavior: no persistent state. It only reads or references process/thread metadata exposed by the C library or kernel headers.

Dependencies and integration points: used to decide whether stress-ng can compile rseq slice/yield helpers and related scheduler instrumentation.

Risks and test signals: rseq support varies by libc, kernel headers, architecture, and link mode. Successful compilation/linking does not prove the running kernel has enabled rseq for the process.
