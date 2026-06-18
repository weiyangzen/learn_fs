<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/attic/test/mmap_offset_decode.c -->
# sources/test-tools/strace/attic/test/mmap_offset_decode.c

Purpose: historical mmap offset decoder probe for architectures/syscalls where mmap offsets are page-based versus byte-based.

Important logic: defines large-file macros, includes `sys/mman.h`, then calls `mmap` with anonymous private mapping and a large offset expression `0x7fff0000LL * 0x1000`. Return value is ignored; process exits based on `errno`.

Control flow: single syscall intended to be observed under strace.

State and persistence: creates at most an anonymous mapping in process memory; no persistent files.

Dependencies and integration: uses Linux mmap behavior and strace syscall argument decoding.

Risks: checking `errno` without first checking `mmap` return can be misleading because successful calls do not reset errno. Anonymous mappings may ignore offset on some platforms. Test signals: strace output should show byte offsets consistently for mmap variants.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/attic/test/mmap_offset_decode.c -->
