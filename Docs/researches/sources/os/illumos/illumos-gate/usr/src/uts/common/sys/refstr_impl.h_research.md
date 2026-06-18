# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/refstr_impl.h

## Role

`refstr_impl.h` defines the private implementation layout for `refstr_t`.

## Layout

`struct refstr` contains:
- `rs_size`: allocation size.
- `rs_refcnt`: reference count.
- `rs_string[1]`: start of the stored constant string.

The comment states that no allocation should exceed 4 GiB, matching the 32-bit size field.

## Research Notes

This header is for implementation code, not ordinary consumers. The public header intentionally hides this layout, so dependencies on `rs_size`, `rs_refcnt`, or trailing-string allocation should stay inside refstr internals.
