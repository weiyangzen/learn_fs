# File Research: sources/windows/reactos/drivers/filesystems/ntfs/finfo.c

Read status: complete file, 786 lines.

This file implements file information query/set operations.

Key query helpers:
- `NtfsGetStandardInformation()` returns allocation size, EOF, link count, delete-pending false, and directory flag.
- `NtfsGetPositionInformation()` returns `FileObject->CurrentByteOffset`.
- `NtfsGetBasicInformation()` returns timestamps and converted file attributes from the FCB filename entry.
- `NtfsGetNameInformation()` returns the FCB path name with overflow handling.
- `NtfsGetInternalInformation()` returns the MFT index.
- `NtfsGetNetworkOpenInformation()` returns timestamps, sizes, and attributes.
- `NtfsGetStreamInformation()` walks data attributes and formats stream entries.
- `NtfsQueryInformation()` dispatches supported query classes and reports unsupported classes.

Key set helpers:
- `NtfsSetEndOfFile()` loads the file record, validates truncation through `MmCanFileBeTruncated()`, finds the selected `$DATA` stream, calls `SetAttributeDataLength()`, then updates the parent directory filename index size fields through `UpdateFileNameRecord()`.
- `NtfsSetInformation()` supports `FileEndOfFileInformation` and a hacky `FileAllocationInformation` path that delegates to EOF handling. Other classes return `STATUS_NOT_IMPLEMENTED`.

Important dependencies:
- FCB/resource locking from `fcb.c`.
- Attribute mutation: `FindAttribute`, `SetAttributeDataLength`, `AttributeDataLength`, `AttributeAllocatedLength`.
- Directory index update: `UpdateFileNameRecord`.

Notable behavior and risks:
- `GetInfoClassName()` indexes a static name table directly with the information class value; unexpected enum values can index out of range.
- Stream enumeration constructs names manually as `:<name>:$DATA`; the memory copy length includes suffix length while copying from the attribute name area, which is risky for named streams.
- Set operations acquire the FCB main resource shared in `NtfsSetInformation()`, while the operation mutates file size and metadata.
- Hardlink support is incomplete: EOF updates only the “best” filename/parent index, with a TODO to update all filename attributes.
