# sources/test-tools/strace/src/get_robust_list.c

Decoder for `get_robust_list`. It prints pid on entry and, on exit, prints the robust-list head pointer and length pointer outputs. State is syscall phase and output memory. Dependencies are pid printers, pointer/number fetch helpers, and process-id type handling. Risks are output pointers on failed syscalls, pid namespace rendering, and pointer-size differences. Tests should cover self pid, other pid, null/bad output pointers, failure cases, and compat pointer widths.
