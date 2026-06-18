# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/tst_bitops.c

Tests low-level bit operation helpers. It verifies `ext2fs_test_bit`, `ext2fs_set_bit`, `ext2fs_clear_bit`, fast set/clear variants, and their 64-bit equivalents against a known byte array and expected bit list.

It also allocates a large scratch array and tests a high bit number `((1U << 31) + 42)`, confirming that both regular and fast 32/64-bit bit operations address large bit indexes correctly. Failures print details and exit nonzero.
