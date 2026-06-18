# File Research: sources/os/linux/linux-stable/fs/ntfs/logfile.c

## Summary
Implements NTFS `$LogFile` restart-page validation and clean-log emptying. It verifies restart-page headers, restart areas, log client arrays, selects the newest valid restart page, and can overwrite a clean LogFile with `0xff` bytes.

## Main Responsibilities
- Validate restart page size, position, version, update sequence array, restart area offset, and chkdsk marker rules.
- Validate restart-area bounds, client-array bounds, sequence-number bits, and alignment fields.
- Validate free/in-use log client linked lists for bounds and loops.
- Load and multi-sector-transfer deprotect complete restart pages.
- Search the LogFile for restart pages and choose the most recent valid page by LSN.
- Empty a clean LogFile by writing `0xff` over mapped non-hole clusters.

## Key APIs
- `ntfs_check_logfile()`.
- `ntfs_empty_logfile()`.
- Internal validation helpers: `ntfs_check_restart_page_header()`, `ntfs_check_restart_area()`, `ntfs_check_log_client_array()`, `ntfs_check_and_load_restart_page()`.

## Important Behavior
Only LogFile version 1.1 is supported. Validation focuses on restart pages and does not replay or fully validate log record pages. Empty LogFiles are accepted and marked with `NVolLogFileEmpty`. If two restart pages are present, the one with the higher current/chkdsk LSN is kept.

`ntfs_empty_logfile()` assumes the journal has already been checked and found clean. It truncates cached LogFile pages, maps runlist fragments as needed, skips holes, writes a cluster-sized `0xff` buffer directly to the block device for each real cluster, waits for the first write range to catch serious I/O errors, and then marks the volume LogFile-empty.

## State and Synchronization
Uses the LogFile inode mapping, `NVolLogFileEmpty`, runlist write locking, `size_lock` for initialized size, block-device mapping readahead, direct block-device writes, and volume error flags.

## Risks
The checker intentionally ignores log record replay, so mount decisions depend on restart-page cleanliness rather than full transaction recovery. Emptying during mount bypasses normal attribute write helpers; runlist corruption or write failure sets volume errors and instructs chkdsk.
