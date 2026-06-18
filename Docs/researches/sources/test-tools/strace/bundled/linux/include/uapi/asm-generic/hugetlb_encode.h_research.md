<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/asm-generic/hugetlb_encode.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/asm-generic/hugetlb_encode.h

Purpose: shared UAPI macros for encoding huge page sizes in syscall flag bitfields.

Important declarations: `HUGETLB_FLAG_ENCODE_SHIFT` is 26 and `HUGETLB_FLAG_ENCODE_MASK` is `0x3f`. Defines encoded constants for 16KB, 64KB, 512KB, 1MB, 2MB, 8MB, 16MB, 32MB, 256MB, 512MB, 1GB, 2GB, and 16GB as `log2(size) << shift`.

Control flow: include guard and macro definitions only.

State and persistence: compile-time constants.

Dependencies and integration: system-call-specific headers can alias these for `MAP_HUGE_*` or similar flags; strace uses them to decode hugepage flag values.

Risks: encoded values are not powers of two but shifted log2 values, so decoders must not treat them like independent bit flags. Test signals: decode mmap/memfd hugepage flags and verify size names match encoded log2 values.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/asm-generic/hugetlb_encode.h -->
