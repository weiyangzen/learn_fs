## sources/security-integrity/ecryptfs-utils/tests/kernel/mmap-close/test.c

Purpose: C reproducer for dirtying a shared mmap after closing the file descriptor. It creates/truncates a file to 32 KiB, maps it writable, closes the fd, fills the mapping with `0xFF`, and unmaps.

Important APIs and functions: `main`, `open(O_RDWR|O_TRUNC|O_CREAT)`, `ftruncate`, `mmap(MAP_SHARED)`, `close`, `memset`, `munmap`. Control flow validates one path argument, prepares the file, maps it, closes before dirtying, writes page-sized chunks, then relies on `munmap` to flush.

State and persistence: Mutates file contents through the VM mapping, with persistence validated by the shell wrapper. Dependencies are POSIX mmap semantics and eCryptfs writeback correctness. Risks include returning raw `errno` values, which are useful but not normalized; failure can represent open/truncate/map/unmap errors or the kernel regression. Test signal is zero when the dirty-close sequence completes without syscall errors.
