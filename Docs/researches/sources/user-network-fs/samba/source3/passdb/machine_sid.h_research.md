# sources/user-network-fs/samba/source3/passdb/machine_sid.h

## Purpose

`machine_sid.h` declares the global SAM SID interface exported by `machine_sid.c`. It is a narrow header used by passdb code that needs to obtain or test the local SAM/domain SID without knowing the secrets DB generation and migration details.

## APIs

The header declares `struct dom_sid *get_global_sam_sid(void)`, `void reset_global_sam_sid(void)`, `bool sid_check_is_our_sam(const struct dom_sid *sid)`, and `bool sid_check_is_in_our_sam(const struct dom_sid *sid)`.

## Integration Points

Callers include SID/RID composition helpers, group mapping, passdb backend interface code, account serialization, and secrets code that invalidates the cache after storing a SID. The header relies on prior declarations of `struct dom_sid` and `bool` from Samba common headers.

## Risks And Test Signals

Because the header exposes a mutable pointer to cached global state, callers must not free or mutate it. Tests around users of this header should verify cache invalidation through `reset_global_sam_sid()`, correct exact-SAM and in-SAM membership checks, and safe behavior when the backing secrets DB changes.
