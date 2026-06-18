# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/bitmap.h

This header defines low-level bitmap operations over vectors of `ulong_t`, plus 32-bit word variants on LP64. It provides sizing/indexing macros (`BT_BITOUL`, `BT_SIZEOFMAP`, `BT_WIM`, `BT_BIW`), public bit operations (`BT_TEST`, `BT_SET`, `BT_CLEAR`), and single-word helpers such as `BIT_ONLYONESET` and `BITX`.

Kernel/fake-kernel builds expose bitmap scanning and utility routines (`bt_availbit`, `bt_gethighbit`, `bt_range`, `highbit`, `highbit64`, `lowbit`, `bt_getlowbit`, `bt_copy`, `odd_parity`) and atomic bit mutation macros backed by `<sys/atomic.h>`. Consumers must perform bounds checking and track bitmap sizes themselves.
