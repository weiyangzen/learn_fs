# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/avscan/filter/csvfs.c

CSVFS-specific support for the AV minifilter. It explains CSVFS architecture, avoids scanning internal CSV downlevel opens, detects hidden CSV NTFS disks, and uses CSVFS revision numbers to decide when a stream may have changed on another cluster node.

Key responsibilities:
- `AvIsVolumeOnCsvDisk` sends `IOCTL_DISK_GET_CLUSTER_INFO` to the disk stack and returns true when the disk is CSV and not in maintenance mode.
- `AvIsCsvDlEcpPresent` detects `GUID_ECP_CSV_DOWN_LEVEL_OPEN` and is used by create filtering to skip CSVFS internal opens.
- `AvPreCreateCsvfs` adds a `GUID_ECP_CSV_QUERY_FILE_REVISION` ECP on CSVFS creates so CSVFS can return revision numbers.
- `AvPostCreateCsvfs` reads acknowledged revision ECP data, compares volume/cache/file revision numbers with the stream context, and marks the stream modified when a rescan is needed.
- `AvPreCleanupCsvfs` queries current revision numbers via `FSCTL_CSV_CONTROL` and applies the same rescan/update decision before cleanup.
- `AvAddCsvRevisionECP`, `AvFindAckedECP`, `AvReadCsvRevisionECP`, and `AvQueryCsvRevisionNumbers` implement ECP and FSCTL plumbing.

Rescan policy:
- Rescan is forced if any revision number is zero, unavailable, or differs from the stream context’s stored revision.
- Revision mismatch is intentionally pessimistic because another node can change the file without this filter instance seeing ordinary write I/O.
- Valid new revisions are returned to the caller for storage after a successful scan.

Dependencies:
- Filter Manager ECP APIs, CSVFS ECP GUIDs, `FSCTL_CSV_CONTROL`, `CSV_CONTROL_PARAM`, `CSV_QUERY_FILE_REVISION`, disk cluster IOCTLs from `ntdddisk.h`, and stream/instance contexts.

Research notes:
- The top comment is important design guidance: filters on hidden NTFS/MUP stacks must avoid CSVFS downlevel opens, and hidden NTFS filters can cause cache coherency or corruption issues.
- The code intentionally treats missing instance context as a reason to rescan rather than trust stale state.
