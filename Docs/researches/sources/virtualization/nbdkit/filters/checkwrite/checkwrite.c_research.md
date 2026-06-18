# File Research: sources/virtualization/nbdkit/filters/checkwrite/checkwrite.c

Purpose: verification filter that accepts write-like requests only when they match existing backend data.

Key details:
- Opens the backend read-only but advertises write, flush, FUA, trim, zero, fast-zero, and multi-conn support.
- `.pwrite` reads the target range from the backend and compares it to the supplied write buffer; mismatch returns `EIO`.
- Debug flag `checkwrite_debug_showdiffs` can emit hexdiffs on mismatches.
- `.flush` is a no-op.
- `.trim` and `.zero` are handled by `checkwrite_trim_zero`, which verifies the backend already reads as zero.
- Uses extents when available to skip known-zero regions and only read/check nonzero extents.
- Fast zero is rejected with `ENOTSUP` if checking would require actual reads.

Integration notes:
- Useful for validating copy/convert tools by proving write requests match a read-only expected image without mutating it.
