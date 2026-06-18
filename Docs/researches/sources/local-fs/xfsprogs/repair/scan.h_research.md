# File Research: sources/local-fs/xfsprogs/repair/scan.h

Header for scanner entry points and reusable inode-hosted btree scan callbacks.

Exports:
- `set_mp` to set the scanner mount context.
- `scan_lbtree` generic long-format btree traversal.
- `scan_bmapbt` inode block-map btree validator.
- `scan_ags` top-level AG scanner.
- `struct rmap_priv` and `struct refc_priv` scanner-private state used by realtime btree scanners and repair code.
- `process_rtrmap_reclist`, `scan_rtrmapbt`, `process_rtrefc_reclist`, and `scan_rtrefcbt` for validating realtime rmap/refcount records and btrees.

The header lets inode repair and realtime metadata code reuse scanner logic for inode-hosted metadata btrees.
