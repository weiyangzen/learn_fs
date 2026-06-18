# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/zio_checksum.c

## Purpose

`zio_checksum.c` implements ZFS checksum selection, checksum generation, checksum verification, checksum context-template management, and special handling for embedded checksums, gang headers, labels, dedup, nopwrite, salted checksums, and encrypted block MAC truncation.

## Major Responsibilities

- Defines `zio_checksum_table[]`, the table of supported checksum algorithms and flags.
- Provides ABD-based Fletcher-2 and Fletcher-4 implementations.
- Maps checksum algorithms to feature flags through `zio_checksum_to_feature()`.
- Resolves inherited/on checksum values through `zio_checksum_select()`.
- Resolves dedup checksum settings through `zio_checksum_dedup_select()`.
- Computes checksums through `zio_checksum_compute()`.
- Verifies checksums through `zio_checksum_error_impl()` and `zio_checksum_error()`.
- Frees per-SPA checksum templates through `zio_checksum_templates_free()`.

## Checksum Table

The table includes:

- `inherit`, `on`, `off`
- `label`
- `gang_header`
- `zilog`
- `fletcher2`
- `fletcher4`
- `sha256`
- `zilog2`
- `noparity`
- `sha512`
- `skein`
- `edonr`

Each entry stores native/byteswap functions, optional template init/free callbacks, flags, and display name.

Important flags include:

- `ZCHECKSUM_FLAG_METADATA`
- `ZCHECKSUM_FLAG_EMBEDDED`
- `ZCHECKSUM_FLAG_DEDUP`
- `ZCHECKSUM_FLAG_SALTED`
- `ZCHECKSUM_FLAG_NOPWRITE`

## ABD Checksum Functions

`abd_checksum_off()` writes a zero checksum.

`abd_fletcher_2_native()` and `abd_fletcher_2_byteswap()` iterate an ABD with Fletcher-2 native or byteswap increment functions.

`abd_fletcher_4_native()` and `abd_fletcher_4_byteswap()` use the active Fletcher-4 ABD ops structure, allowing platform-specific optimized implementations.

## Selection Logic

`zio_checksum_select()` treats child `inherit` as parent and child `on` as `ZIO_CHECKSUM_ON_VALUE`.

`zio_checksum_dedup_select()` is similar but maps `on` to `spa_dedup_checksum(spa)` and preserves `ZIO_CHECKSUM_VERIFY` when requested. It asserts that dedup checksums are either dedup-capable, verification-only, or off.

## Embedded Checksum Handling

For embedded checksum algorithms, the checksum is stored in a `zio_eck_t` embedded in the block data rather than only in the block pointer.

Special verifiers:

- Gang header checksum verifier is based on `<vdev, offset, txg>`.
- Label checksum verifier is based on label offset.
- ZILOG2 uses `zil_chain_t.zc_nused` to determine the effective checksum length.

`zio_checksum_compute()` temporarily writes the verifier into the embedded checksum field, computes the checksum, then writes the actual checksum back into the embedded field.

`zio_checksum_error_impl()` temporarily replaces the embedded expected checksum with the verifier, recomputes, restores the expected checksum, and compares.

## Encryption Interaction

Encrypted blocks store a MAC in the upper half of `blk_cksum`, leaving only a truncated regular checksum. `zio_checksum_handle_crypt()` preserves MAC words and, for weaker non-dedup checksums, XORs high checksum words into low words before truncation to retain more entropy.

Verification mirrors that behavior by zeroing MAC words before comparing actual and expected checksums for protected non-objset blocks.

## Context Templates

Some salted or expensive checksum algorithms can initialize a context template per SPA. `zio_checksum_template_init()` lazily initializes templates under `spa_cksum_tmpls_lock`. `zio_checksum_templates_free()` tears them down during SPA destruction.

## Fault Injection

`zio_checksum_error()` calls `zio_checksum_error_impl()` and then, if fault injection is enabled, can inject `ECKSUM` through `zio_handle_fault_injection()`. The bad checksum report records whether an error was injected.

## Key Dependencies

- `zio_checksum_table` is consumed by `zio.c`.
- Fletcher implementations come from `zfs_fletcher`.
- SHA/Skein/EdonR checksum functions are referenced through the table.
- SPA stores checksum salt and initialized templates.
- ABD iteration provides data traversal without requiring linear buffers.

## Notes for Future Readers

- Embedded checksum algorithms destructively modify the checked buffer during compute/verify, but verification restores the expected checksum field.
- `ZIO_CHECKSUM_MASK` must be used before feature lookup when dedup verify bits may be set.
- Gang-header checksums intentionally differ from data checksums so gang metadata can be verified independently.
