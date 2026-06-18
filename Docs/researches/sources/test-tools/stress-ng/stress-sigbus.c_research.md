# sources/test-tools/stress-ng/stress-sigbus.c

Purpose: implements the `sigbus` stressor, generating recoverable bus faults by accessing a file-backed mapping after truncating its backing file, with optional misaligned access attempts on architectures that may fault.

Important APIs/types/functions: `stress_bushandler`, `stress_sigbus`, `sigsetjmp`, `stress_signal_siglongjmp`, `sigaction`, `SA_SIGINFO`, `posix_fallocate`, `ftruncate`, `mmap`, `munmap`, `SIGBUS`, and fallback SIGSEGV handling.

Control flow: the worker creates and unlinks a temp file, allocates two pages, maps them shared, truncates the file to one page, installs SIGBUS and SIGSEGV handlers, synchronizes start, then repeatedly establishes a jump point. On the non-faulting path it sometimes attempts misaligned writes and always accesses the now-unbacked second page. On the signal-return path it optionally verifies signal number, fault address, and SIGBUS `si_code`, then increments bogo ops.

State and persistence behavior: state is an unlinked temp file, a two-page mapping, and global volatile signal info fields. Cleanup unmaps, closes the fd, and removes the temp directory.

Dependencies and integration points: registered as `CLASS_SIGNAL | CLASS_OS`, optional verify when `SA_SIGINFO` exists, and unimplemented without `siglongjmp`. It uses stress-ng filesystem helpers, mmap helpers, and platform guards for optional alignment-fault behavior.

Risks and test signals: platforms may deliver SIGSEGV rather than SIGBUS, which is tolerated. Failure signals include missing fault recovery, wrong fault address/code in verify mode, inability to create backing storage, or cleanup after repeated longjmp paths.
