# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/refstr.h

## Role

`refstr.h` declares the public kernel-facing interface for reference-counted immutable strings.

## Interface

The actual `struct refstr` layout is private. Under `_KERNEL` or `_FAKE_KERNEL`, the API provides:
- `refstr_alloc(const char *)`
- `refstr_value(refstr_t *)`
- `refstr_hold(refstr_t *)`
- `refstr_rele(refstr_t *)`

## Research Notes

This is an intentionally opaque handle API. Consumers should treat returned string values as owned by the `refstr_t` lifetime and should not depend on implementation layout.
