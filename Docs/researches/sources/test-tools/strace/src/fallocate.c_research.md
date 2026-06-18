# sources/test-tools/strace/src/fallocate.c

Decoder for `fallocate`. It prints fd, mode flags from `falloc_flags`, offset, and length using 64-bit argument helpers. There is no persistent state. Dependencies include `<linux/falloc.h>`, xlat tables, and large-argument decoding from `defs.h`. Risks are architecture-specific 64-bit argument splitting and newly added mode flags. Test signals are traces for normal allocation, punch-hole/collapse/zero-range modes, unknown flags, invalid fd failures, and large offset/length values.
