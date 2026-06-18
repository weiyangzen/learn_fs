# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/avscan/filter/csvfs.h

Kernel-private CSVFS interface header for the AV minifilter. It declares the CSVFS hooks used by `avscan.c` and the helper predicates for CSV downlevel opens and CSV disk detection.

Declared interfaces:
- `AvPreCleanupCsvfs`: checks CSVFS revision numbers before cleanup and returns whether stream revision fields should be updated after a successful scan.
- `AvPostCreateCsvfs`: consumes create-time CSVFS revision ECP results and decides whether a rescan is needed.
- `AvPreCreateCsvfs`: adds the CSV revision query ECP during pre-create on CSVFS volumes.
- `AvIsCsvDlEcpPresent`: detects internal CSVFS downlevel-open ECPs.
- `AvIsVolumeOnCsvDisk`: checks whether a volume’s disk is a CSV disk outside maintenance mode.

Dependencies:
- Requires `PFLT_CALLBACK_DATA`, `PCFLT_RELATED_OBJECTS`, `PAV_STREAM_CONTEXT`, and `PFLT_VOLUME` from the kernel AV and Filter Manager context.

Research notes:
- The revision-number out-parameters let generic create/cleanup logic stay mostly filesystem-neutral while still updating CSV-specific coherence metadata after scans.
