<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/attic/test/x32_mmap.c -->
# sources/test-tools/strace/attic/test/x32_mmap.c

Purpose: x32 ABI probe for `mmap` offset width and unit handling.

Important logic: opens `/etc/passwd`, invokes raw `syscall(__NR_mmap | 0x40000000, start=0, len=0x10000, PROT_READ, MAP_SHARED, fd=0, ofs=0x12345670000)`, prints return/errno, then dumps `/proc/<pid>/maps` to show the mapped file offset.

Control flow: one raw mmap syscall followed by procfs maps read.

State and persistence: creates a read-only shared mapping of `/etc/passwd`; no persistent changes.

Dependencies and integration: x86/x32 syscall numbering, procfs maps, and strace mmap decoder.

Risks: x32 support may be disabled. Offset must remain page-aligned. Reading maps into a fixed 16 KiB buffer can truncate output. Test signals: `/proc/<pid>/maps` and strace should show the large byte offset, not a page-shifted or truncated value.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/attic/test/x32_mmap.c -->
