<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/syscallent.h -->
# sources/test-tools/strace/src/linux/x86_64/syscallent.h

Purpose: primary x86_64 syscall table for native personality 0.
Important APIs/types/functions: `sysent` initializer rows with argument counts, classification flags, `SEN` decoder selectors, and names; includes `syscallent-common.h`.
Control flow: no executable code; indexed by normalized syscall number during syscall dispatch. State and persistence behavior: static build artifact.
Dependencies and integration points: all x86_64 syscall decoding depends on correct entries and flags. Risks: stale syscall additions, wrong argument count, or missing flags affect filtering and output. Test signals: generated syscall table diff checks and syscall-specific tests through newest entries such as `statx`, `rseq`, and `uretprobe`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/syscallent.h -->
