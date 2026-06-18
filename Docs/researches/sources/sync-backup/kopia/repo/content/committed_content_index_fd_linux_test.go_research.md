# sources/sync-backup/kopia/repo/content/committed_content_index_fd_linux_test.go

Purpose: Linux-specific regression test ensuring mmap-backed disk index cache does not retain a file descriptor for every opened index.

Important APIs/types/functions: `countFDsLinux` reads `/proc/self/fd`; `TestCommittedContentIndexCache_Disk_FDsNotGrowingOnOpen_Linux` creates many cached indexes and opens them all.

Control flow: the test creates 200 small index files in a disk cache, counts file descriptors, opens every index and keeps the mappings alive, counts descriptors again, and asserts the delta is at most 32. It then closes all indexes.

State and persistence behavior: `.sndx` cache files live in a temp directory; mmap objects remain alive until closed by the test.

Dependencies/integration: Linux `/proc`, disk cache, mmap behavior from the Unix implementation, index builders, faketime, and test logging.

Risks and edge cases: the test is not parallel to avoid FD noise. The local `var lm *repodiag.LogManager` is nil before `lm.NewLogger("test")`, which appears risky unless `LogManager` methods tolerate nil receivers.

Test signals: a large FD delta would mean Unix mmap no longer closes descriptors promptly, which matters for repositories with many indexes.
