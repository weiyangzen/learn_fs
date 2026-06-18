<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/x32/syscallent.h -->
# sources/test-tools/strace/src/linux/x32/syscallent.h

Purpose: X32 ABI syscall dispatch table. It maps x32 syscall numbers, including entries starting at the x32 compatibility range, to argument counts, tracing flag classes, decoder symbols, and display names.
Important APIs/types/functions: declarative `sysent` initializer rows using `SEN(...)`, flags such as `TD`, `TF`, `TP`, `TM`, `CST`, `CC`, and common include `syscallent-common.h`.
Control flow: there is no executable flow; the table is indexed after personality detection selects x32. Missing or reserved numbers fall back to common strace table handling.
State and persistence behavior: static read-only build data; no runtime state. Dependencies and integration points: consumed by syscall lookup, x86_64/x32 personality plumbing, and decoder implementations named by `SEN`.
Risks: wrong numbering, flags, or compat annotations cause incorrect argument decoding, path/process filtering, or injected-fault behavior. Test signals: x32 syscall-number smoke tests, generated table diff checks, and syscall output tests for high-risk entries such as `execveat`, aio, and vector I/O.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/x32/syscallent.h -->
