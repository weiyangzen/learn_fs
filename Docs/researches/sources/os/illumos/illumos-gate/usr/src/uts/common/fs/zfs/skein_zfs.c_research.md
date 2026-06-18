# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/skein_zfs.c

This file provides ABD-backed Skein MAC checksum support for ZFS. It computes 256-bit outputs from a Skein-512 context template seeded with ZFS checksum salt.

Core responsibilities:
- Defines `skein_incremental()` as an ABD iteration callback that feeds each contiguous buffer segment to `Skein_512_Update()`.
- Implements `abd_checksum_skein_native()` by copying a preinitialized Skein context template, iterating the ABD contents through it, finalizing into `zio_cksum_t`, and zeroing the working context.
- Implements `abd_checksum_skein_byteswap()` by computing the native Skein checksum and byte-swapping the four 64-bit checksum words.
- Provides `abd_checksum_skein_tmpl_init()` to allocate and initialize a keyed Skein-512 context template from `zio_cksum_salt_t`.
- Provides `abd_checksum_skein_tmpl_free()` to zero and free a previously allocated template.

Important control-flow notes:
- `abd_checksum_skein_native()` requires a non-NULL `ctx_template` and asserts that requirement.
- The template is copied per checksum operation so callers can reuse the initialized keyed state without mutation.
- `Skein_512_InitExt()` is configured for `sizeof (zio_cksum_t) * 8` output bits and uses the salt bytes as key material.
- The byteswap implementation relies on Skein being internally endian-insensitive, so only the final `zio_cksum_t` words are swapped.

Key dependencies:
- ABD iteration API for block-buffer traversal.
- Skein-512 implementation and context structures.
- ZFS checksum salt and checksum word types.
- Kernel memory allocation and zeroing helpers.

Risk-sensitive invariants:
- The context template must remain valid for the duration of checksum calls and must be freed through `abd_checksum_skein_tmpl_free()`.
- Working and template contexts contain keyed material and are explicitly zeroed before release.
- Output width must remain 256 bits to match `zio_cksum_t` and ZFS on-disk checksum expectations.
