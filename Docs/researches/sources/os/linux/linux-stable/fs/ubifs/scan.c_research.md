# File Research: sources/os/linux/linux-stable/fs/ubifs/scan.c

## Purpose
Provides generic logical eraseblock scanning used by journal replay, garbage collection, TNC in-the-gaps commit, and debug validation.

## Key Behavior
- `ubifs_scan_a_node()` classifies the next bytes in an LEB as empty space, padding bytes, a valid node, a corrupt node, or a bad padding node.
- Padding is accepted only when it uses `UBIFS_PADDING_BYTE`, has nonzero length, and is 8-byte aligned.
- `ubifs_start_scan()` allocates a scan descriptor and reads the requested LEB range into the caller-provided scan buffer.
- `ubifs_scan()` walks nodes until empty space or corruption, adds each valid scanned node to `sleb->nodes`, then validates that the remaining empty space is all `0xff`.
- `ubifs_add_snod()` records scanned node metadata: sequence number, type, offset, length, and key for keyed leaf nodes.
- `ubifs_scanned_corruption()` reports the failing LEB offset and dumps up to 8192 bytes for diagnostics.
- `ubifs_scan_destroy()` frees scan-node descriptors but not the scan buffer, which belongs to the caller.

## Important Dependencies
- Uses `ubifs_check_node()` for node validation.
- Uses `ubifs_leb_read()` for raw LEB reads.
- Scan results are consumed by recovery, GC, debug checks, and `tnc_commit.c` gap layout.

## Invariants and Risks
- Empty space must begin at a min-I/O aligned offset; otherwise the LEB is treated as needing recovery.
- `-EUCLEAN` signals corruption/recovery-needed rather than ordinary I/O failure.
- Integrity read errors from UBI may be ignored during the initial read because UBIFS validates nodes with CRC/hash checks afterward.
