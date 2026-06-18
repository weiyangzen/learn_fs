# File Research: sources/windows/reactos/drivers/filesystems/ntfs/attrib.c

## Purpose
Implements NTFS attribute construction, mapping-pair/data-run conversion, cluster freeing, attribute enumeration, attribute-list reading, filename/standard-info lookup, and debug dumping for ReactOS NTFS.

## Main Responsibilities

### Attribute Constructors
- `AddBitmap` adds a resident `$BITMAP` attribute with initial 8-byte bitmap payload.
- `AddData` adds an unnamed resident empty `$DATA` attribute.
- `AddFileName` adds a `$FILE_NAME` attribute:
  - Computes parent directory by dissecting the file path and calling `NtfsFindMftRecord`.
  - Sets timestamps and archive/directory attributes.
  - Stores parent file reference and sequence information.
  - Chooses POSIX or WIN32+DOS name type based on case sensitivity and DOS 8.3 legality.
- `AddIndexAllocation` adds a named nonresident `$INDEX_ALLOCATION` attribute with empty mapping pairs.
- `AddIndexRoot` adds a resident named `$INDEX_ROOT` attribute and copies supplied index-root payload.
- `AddStandardInformation` adds `$STANDARD_INFORMATION` with current timestamps and archive attribute.

All constructor helpers only support insertion at the current `AttributeEnd` marker. They update `NextAttributeNumber` and move file-record end markers through `SetFileRecordEnd`.

### Data Run / Mapping Pair Support
- `DecodeRun` decodes NTFS mapping-pair runs into offset and length, including sparse runs as offset `-1`.
- `ConvertDataRunsToLargeMCB` converts encoded data runs to an initialized `LARGE_MCB`.
- `ConvertLargeMCBToDataRuns` converts an MCB back to encoded mapping pairs.
- `FindRun` performs a minimal first-run lookup for a nonresident attribute.
- `GetPackedByteCount` returns the minimal signed/unsigned byte count for mapping-pair encoding.
- `GetLastClusterInDataRun` walks all mapping pairs and returns the last physical cluster.

### Allocation Mutation
- `AddRun` appends allocated clusters to a nonresident attribute:
  - Adds a new MCB entry.
  - Converts MCB to mapping pairs.
  - Expands the attribute if there is room in the file record.
  - Moves trailing attributes when needed.
  - Updates `HighestVCN` and writes the file record.
  - Returns `STATUS_NOT_IMPLEMENTED` if an attribute list would be required.
- `FreeClusters` shrinks a nonresident attribute:
  - Reads the volume `$Bitmap` file.
  - Clears bits for clusters removed from the end of the MCB.
  - Writes the bitmap back.
  - Re-encodes mapping pairs.
  - Shrinks the attribute if it is the final attribute in the record.
  - Updates the file record.

### Attribute Enumeration
- `FindFirstAttribute`, `FindNextAttribute`, and `FindCloseAttribute` iterate attributes in a file record.
- `InternalReadNonResidentAttributes` loads a nonresident `$ATTRIBUTE_LIST`.
- `FindFirstAttributeListItem` and `FindNextAttributeListItem` iterate loaded attribute-list entries.
- `InternalGetNextAttribute` validates attribute lengths and stops on corrupt/out-of-range offsets.

### Lookup Helpers
- `GetFileNameFromRecord` returns a filename attribute of a requested name type, treating WIN32_AND_DOS as either WIN32 or DOS.
- `GetBestFileNameFromRecord` prefers POSIX, then WIN32, then DOS names.
- `GetStandardInformationFromRecord` finds `$STANDARD_INFORMATION`.
- `GetFileNameAttributeLength` computes variable-size filename attribute payload length.

### Debug Dumping
- `NtfsDumpFileAttributes`, `NtfsDumpAttribute`, `NtfsDumpDataRuns`, `NtfsDumpDataRunData`, and type-specific dump helpers print file-record attribute details, names, index-root contents, and mapping pairs.

## Important Interactions
- Relies heavily on NTFS structures and helpers from `ntfs.h` and other NTFS driver files:
  - `ReadFileRecord`
  - `UpdateFileRecord`
  - `FindAttribute`
  - `ReadAttribute`
  - `WriteAttribute`
  - `ReleaseAttributeContext`
  - `NtfsFindMftRecord`
  - `MoveAttributes`
  - `SetFileRecordEnd`
- Uses FsRtl large MCB APIs for run management.
- Uses volume metadata from `Vcb->NtfsInfo`, especially bytes per file record, bytes per cluster, bytes per sector, and cluster count.
- Uses the VCB file-record lookaside list for reading `$Bitmap`.

## Risks / Review Notes
- Many add-attribute paths return `STATUS_NOT_IMPLEMENTED` instead of growing into an `$ATTRIBUTE_LIST` when the file record lacks space.
- `ConvertLargeMCBToDataRuns` has a TODO for holes/sparse runs when encoding MCB entries.
- `FindRun` only decodes the first run and does not search for the run containing the requested VCN.
- `FreeClusters` returns `0` on several failure paths where an `NTSTATUS` error would be clearer.
- `FreeClusters` decrements `HighestVCN` with `min(current, current - 1)`, despite the comment saying not to go below zero; this deserves review for underflow/negative behavior.
- `AddRun` allocates a new attribute-context record without checking allocation failure before copying.
- Debug dump routines recursively print data runs and assume valid on-disk structures; they are diagnostic rather than hardened parsing paths.
