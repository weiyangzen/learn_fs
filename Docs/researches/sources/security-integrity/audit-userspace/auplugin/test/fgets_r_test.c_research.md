<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auplugin/test/fgets_r_test.c -->
# sources/security-integrity/audit-userspace/auplugin/test/fgets_r_test.c

Purpose: unit test for the reentrant `auplugin_fgets_state_t` API, including custom buffer ownership and mmap-file mode.

Important APIs and functions: `test_basic_state` covers init/more/eof/read/clear/destroy; `test_deferred_compaction` uses `auplugin_setvbuf_r` with `MEM_MALLOC`; `test_reject_self_managed_override` validates invalid ownership rejection; `test_mmap_file` maps auparse `test.log` and reads it through `MEM_MMAP_FILE`.

Control flow and state: tests use pipes for synthetic streams, a heap custom buffer, and a private mmap of a fixture file. Each test owns and destroys its state object, preventing cross-test global contamination.

Dependencies and integration: includes `auplugin.h`, POSIX pipe/read/write, mmap/stat/open, and fixture path resolution via `srcdir`.

Risks and test signals: catches reentrant EOF semantics, compaction, buffer ownership, and mmap traversal. It assumes `test.log` has 14 lines and starts with `type=AVC`, so fixture drift requires test updates. Passing prints `audit-fgets_r tests: all passed`.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auplugin/test/fgets_r_test.c -->
