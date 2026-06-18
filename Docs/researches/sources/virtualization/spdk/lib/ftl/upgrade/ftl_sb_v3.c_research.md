# File Research: sources/virtualization/spdk/lib/ftl/upgrade/ftl_sb_v3.c

Helpers for v3 superblock metadata layout.

Behavior:
- Checks v3 magic and empty layout status.
- Validates linked metadata-region pointers stay inside the fixed superblock buffer.
- `ftl_superblock_v3_md_layout_load_all()` walks linked v3 region records, skips free records, rejects fixed/invalid types, detects duplicate versions and loops, and loads the oldest region version per type into `dev->layout`.
- Requires all v3 region types to be found.
- Dumps v3 linked layout records for diagnostics.

Risk:
- Loop detection is based on a sentinel for non-monotonic `df_next`; malformed but monotonic cycles are impossible in bounded superblock memory if overflow checks hold.
