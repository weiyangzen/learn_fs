# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/dkioc_free_util.c

## Purpose

`dkioc_free_util.c` provides shared helpers for the `DKIOCFREE` ioctl, which lets callers tell block devices that byte ranges are no longer needed. It is built for both kernel use and `libzpool` builds, and focuses on safe copyin, variable-length list lifetime, extent alignment, validation, and segmentation for devices with trim/free constraints.

## Main Interfaces

- `dfl_copyin()` copies a variable-length `dkioc_free_list_t` from user or kernel space and validates the extent count.
- `dfl_free()` releases a list allocated or consumed by these helpers.
- `dfl_iter()` consumes a free-list request, validates and adjusts it to `dkioc_free_info_t` device limits, and invokes a caller callback with one or more conforming lists.

Private helpers are:

- `adjust_exts()` to align starts and lengths and validate device bounds.
- `process_range()` to build a new list from a contiguous subset of extents while dropping zero-length entries.
- `split_extent()` to split one oversized extent into callback-sized single-extent requests.

## Copyin And Lifetime

`dfl_copyin()` handles two caller models. With `FKIOCTL`, the input pointer is already in kernel space and the function copies from it directly. Otherwise it first copies only `dfl_num_exts`, validates it against `DFL_COPYIN_MAX_EXTS`, allocates the precise `DFL_SZ(num_exts)` buffer, and copies the full list. It also rechecks that the copied structure still has the expected `dfl_num_exts`.

`dfl_iter()` is explicitly consuming: after successful callback transfer of an unmodified list, the callback owns it; otherwise `dfl_iter()` frees the original list before returning. Newly allocated sublists are owned by the callback.

## Validation And Alignment

`dfl_iter()` validates device constraints before touching extents:

- `dfi_bshift` must represent a block size from 512 bytes through `1 << 30`.
- `dfi_max_bytes`, `dfi_align`, and `dfi_max_ext_bytes` must be block-size aligned when nonzero.
- `dfi_align` must be nonzero.
- A single-extent maximum cannot exceed the total-request maximum.

`adjust_exts()` applies `dfl_offset` before alignment, detects overflow in start and end calculations, rejects extents beyond `max_off`, rounds starts up to `dfi_align`, rounds ends down to the device block size, then stores adjusted starts relative to `dfl_offset`. Extents that become too small are converted to zero length rather than failing the whole ioctl.

## Segmentation Behavior

After adjustment, `dfl_iter()` walks original extent order while accumulating a request window. It emits callback batches when:

- one extent exceeds `dfi_max_ext_bytes`,
- adding an extent would exceed `dfi_max_bytes`,
- adding an extent would exceed `dfi_max_ext`.

Large extents are handled by `split_extent()`, which uses `dfi_max_ext_bytes` first, then `dfi_max_bytes`, then `UINT64_MAX` as the segment length. It aligns split points so subsequent chunks start on acceptable boundaries.

`process_range()` removes zero-length extents from emitted sublists. If all extents in the range are zero length, no callback is made and success is returned.

## Error Semantics

The helper follows the coarse `DKIOCFREE` model: malformed or out-of-device input fails the whole request, but ranges narrowed away by alignment are silently ignored. Callback errors abort iteration and are returned to the caller. Allocation failures return `ENOMEM`; invalid geometry or extents return `EINVAL`; arithmetic overflow returns `EOVERFLOW`.

## Dependencies

This file depends on `sys/dkio.h` and `sys/dkioc_free_util.h` for structures and macros, DDI copyin flags, kernel memory allocation, power-of-two alignment macros, and `SET_ERROR()` conventions. It includes SDT support but the file itself does not define probes.

## Notable Invariants And Audit Notes

- `dfl_num_exts` must be nonzero and bounded before `DFL_SZ()` allocation.
- All callback lists emitted by `dfl_iter()` conform to the caller-provided `dkioc_free_info_t`.
- The original request is freed by `dfl_iter()` except for the fast path where it is handed directly to the callback.
- `process_range()` assumes the callback takes ownership of each allocated `new_dfl`.
- The utility intentionally cannot report partial completion; callers should treat success as "all valid, processable ranges were submitted."
