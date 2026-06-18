# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/of/ofa_solaris.h

## Purpose

Provides a small Solaris kernel wrapper type used by OFED-style user/kernel interfaces to pass response addresses in a way compatible with 32-bit and 64-bit layouts.

## Main Definitions

- Kernel-only include of basic types and byteorder.
- `ofv_resp_addr_t`: union of a 64-bit response address and two 32-bit words.
- Macros:
  - `r_laddr` accesses the full 64-bit value.
  - `r_addr` and `r_notused` select the correct 32-bit word depending on `_LONG_LONG_HTOL`.

## Integration Notes

Included by `ofed_kernel.h` and `ib_user_verbs.h` to model OFED uverbs response pointer/address fields without direct pointer types.

## Risks and Gotchas

- Word selection depends on long-long byte ordering, not ordinary integer byte order.
- Only active under `_KERNEL`; userland consumers need matching ABI definitions elsewhere.
