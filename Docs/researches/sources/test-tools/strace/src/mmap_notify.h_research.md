<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/mmap_notify.h -->
# sources/test-tools/strace/src/mmap_notify.h

Purpose: declares mmap notification callback API.
Important APIs/types/functions: `mmap_notify_fn`, `mmap_notify_register_client`, and `mmap_notify_report`.
Control flow: no implementation. State and persistence behavior: exposes process-global registration contract implemented in `mmap_notify.c`.
Dependencies and integration points: memory syscall decoders notify cache clients after mapping changes. Risks: callbacks must tolerate being called from syscall decoding paths. Test signals: compile and integration tests with mmap cache enabled.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/mmap_notify.h -->
