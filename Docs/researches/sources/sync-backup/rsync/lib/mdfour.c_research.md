# sources/sync-backup/rsync/lib/mdfour.c

Purpose: implements MD4 for legacy rsync checksum modes and SMB-derived compatibility behavior.

Important APIs/types/functions: public `mdfour_begin`, `mdfour_update`, `mdfour_result`, optional `mdfour` test helper, static global `m`, and helpers `mdfour64`, `copy64`, `copy4`, and `mdfour_tail`.

Control flow: `mdfour_begin` initializes MD4 state. `mdfour_update` assigns the global context pointer, processes full 64-byte chunks with `copy64` and `mdfour64`, updates bit counters for full chunks, and calls `mdfour_tail` for the final partial chunk or zero-length finalization. `mdfour_tail` pads into one or two 64-byte blocks, writes total bit count, and preserves the pre-protocol-27 behavior of omitting the high length word. `mdfour_result` writes little-endian A/B/C/D into the digest.

State and persistence behavior: digest state is caller-owned `md_context`, but compression uses a file-static `md_context *m`, making the implementation non-reentrant and not thread-safe. It also reads global `protocol_version` inside final padding, so the same input can hash differently for old protocol compatibility.

Dependencies/integration: includes `rsync.h`; used by checksum negotiation and legacy checksum paths. `TEST_MDFOUR` includes a standalone file checksum program and sets `protocol_version = 28`.

Risks/test signals: MD4 is cryptographically broken but retained for compatibility. Risks include the global context pointer, protocol-version-dependent finalization, and special handling for inputs whose length is a multiple of 64 in the test path. Tests should cover protocol 26 vs 27+ outputs, zero-length finalization, exact 55/56/64-byte boundaries, and concurrent/reentrant exclusion assumptions.
