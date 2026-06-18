# File Research: sources/os/darwin/xnu/bsd/vfs/vfs_cprotect.c

## Scope

This file implements VFS-side content-protection key container helpers and key-store notification plumbing. It manages `cpx_t` allocation, key material storage, AES-IV context generation, copy/flush/free behavior, filesystem notification of device lock/EP/CX state changes, protection-class validation, and cached parsing of the kernel `osversion`.

## Public And Internal APIs Covered

- CPX sizing/lifetime: `cpx_size()`, `cpx_sizex()`, `cpx_alloc()`, `cpx_alloc_ctx()`, `cpx_free_ctx()`, `cpx_writeprotect()`, `cpx_free()`, `cpx_init()`.
- CPX flags/accessors: SEP-wrapped key, composite key, offset IV, synthetic-offset IV, key length, key presence, and key pointer APIs.
- IV context APIs: `cpx_set_aes_iv_key()` and `cpx_iv_aes_ctx()`.
- Key state mutation: `cpx_flush()`, `cpx_can_copy()`, `cpx_copy()`.
- Key-store actions: `cp_key_store_action()` and `cp_key_store_action_for_volume()`.
- Validation/version helpers: `cp_is_valid_class()` and `cp_os_version()`.

## Control Flow And Behavior

`cpx_alloc()` uses either page allocation with optional write protection under `CONFIG_KEYPAGE_WP` or zone allocation from `cpx_zone` otherwise. Non-write-protected builds allocate an optional AES context from `aes_ctz_zone` when requested. `cpx_init()` clears flags, sets key length to zero, and records the maximum key length.

`cpx_iv_aes_ctx()` lazily derives a 128-bit AES IV context by SHA1 hashing cached key material, using the digest as AES key input, and tagging the context as VFS-generated. Changing key length clears VFS IV context bits so a later IV request regenerates state.

`cp_key_store_action*()` builds a callback argument and walks mounts with `vfs_iterate()`. The callback optionally filters by filesystem UUID and dispatches `FIODEVICELOCKED`, `FIODEVICEEPSTATE`, or `FIODEVICECXSTATE` through `VFS_IOCTL()`.

## State And Data Structures

- `struct cpx` is variable length and stores flags, max/current key length, optional AES context pointer, and key bytes.
- Debug builds add leading/trailing magic checks.
- Zones: `cpx_zone` clears freed fixed CPX storage; `aes_ctz_zone` clears AES contexts.
- Callback state is carried by `cp_vfs_callback_arg`, including optional UUID filtering.

## Dependencies

Depends on content-protection headers, mount iteration and VFS ioctl dispatch, SHA1 and AES helpers, kernel zones, and optional VM page protection APIs under `CONFIG_KEYPAGE_WP`.

## Risks And Invariants

- Key material and AES contexts are explicitly zeroed on flush/free paths; this is a confidentiality invariant.
- `cpx_copy()` assumes destination AES context exists if initialized flags are copied.
- In `CONFIG_KEYPAGE_WP` builds, `cpx_alloc()` sets `CPX_WRITE_PROTECTABLE` before calling `cpx_init()`, while `cpx_init()` clears flags. The write-protection/free paths depend on that flag, so this ordering is a sensitive invariant.
- `cp_vfs_callback()` silently ignores mounts without UUID support or mismatched UUIDs.
- `parse_os_version()` accepts only versions shaped like digits, one letter, digits; parse failure caches sentinel value `1`.
