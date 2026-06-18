# File Research: sources/local-fs/ntfs-3g/libntfs-3g/logfile.c

## Purpose
Validates and optionally clears NTFS `$LogFile`, enough to decide whether the volume journal indicates clean shutdown. It checks restart pages and restart areas, not full log replay.

## Main Interfaces
- `ntfs_check_logfile()` validates `$LogFile` and returns the most recent valid restart page.
- `ntfs_is_logfile_clean()` checks clean-shutdown state from the restart area.
- `ntfs_empty_logfile()` overwrites a clean non-resident `$LogFile` with `0xff` bytes and marks it empty.
- Internal validators check restart page headers, restart areas, log client arrays, and load/deprotect restart pages.

## Control Flow
`ntfs_check_logfile()` caps size, verifies minimum size, scans candidate restart page positions, reads the first NTFS block, accepts `RSTR` or `CHKD` pages, validates header/area/client lists, loads and MST-deprotects the full page, and chooses the page with the newer LSN. Empty logfiles set the volume empty flag and pass.

`ntfs_is_logfile_clean()` treats an already-empty logfile as clean; otherwise it requires valid restart magic and either no active clients or `RESTART_VOLUME_IS_CLEAN`.

## Integration Points
Uses `ntfs_attr_pread/pwrite`, MST fixups from `mst.c`, logfile layout structures, and volume flags such as `NVolLogFileEmpty`.

## Risks and Invariants
- Version support is limited to `$LogFile` 1.1 and 2.0, with 2.0 still treated carefully.
- Chkdsk-modified restart pages may lack update sequence arrays.
- The implementation is intentionally conservative and may classify some idle unclean shutdowns as dirty.
- `ntfs_empty_logfile()` requires a prior clean check and rejects resident `$LogFile`.
