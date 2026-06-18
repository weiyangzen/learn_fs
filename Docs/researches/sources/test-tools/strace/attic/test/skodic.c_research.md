<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/attic/test/skodic.c -->
# sources/test-tools/strace/attic/test/skodic.c

Purpose: demonstrates pathname races where strace may print a path different from the file the kernel actually opened.

Important logic: creates a temporary file, maps one page shared, writes `/etc/shadow`, verifies it cannot be opened, then forks. Child loops alternating the mapped string between `/etc/passwd` and `/etc/shadow`; parent loops opening the same pointer.

Control flow: shared memory mutation races with kernel copying the pathname for `open`.

State and persistence: creates a temporary file and shared mapping; opens/closes system paths; no intended persistent modifications.

Dependencies and integration: requires mmap, fork, GNU `error`, and strace path decoding options such as `-y`/`-eopen`.

Risks: intentionally tries to race privileged path display and can produce alarming output. Infinite loops require timeout. Test signals: running under timeout and grep can reveal successful opens printed with the wrong raced pathname.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/attic/test/skodic.c -->
