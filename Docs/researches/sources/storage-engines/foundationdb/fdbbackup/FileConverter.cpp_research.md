# sources/storage-engines/foundationdb/fdbbackup/FileConverter.cpp

## Purpose
Implements `fdbconvert`, a tool that converts partitioned backup mutation logs over a version range into the older backup log format.

## Important APIs, Types, and Functions
`ConvertParams` stores CLI state. `getRelevantLogFiles()` filters/deduplicates logs. `MutationFilesReadProgress` opens files and yields globally ordered `VersionedData`; nested `FileProgress::decodeBlock()` parses `PARTITIONED_MLOG_VERSION` blocks. `LogFileWriter` writes old-format mutation log blocks. `convert()` orchestrates the conversion.

## Control Flow
`main()` parses options, enables tracing, initializes network, and runs `convert()`. Conversion opens the backup container, lists/describes files, filters logs, decodes selected files to the begin version, repeatedly merges the next mutation by version/subsequence, groups mutations by commit version, writes old-format batches, and finishes the output file.

## State and Persistence Behavior
Read state is per-file offset/EOF/buffered mutations. Output persistence is a new log file in the backup container, padded and block-delimited according to old backup format. No database transaction state is used.

## Dependencies and Integration Points
Depends on backup container APIs, `BackupAgent`, `MutationList`, Flow async files, serialization, client knobs, trace logging, and options from `FileConverter.h`. Built as `fdbconvert`.

## Risks
Corrupt or incompatible serialized logs throw restore errors. Large ranges can use many descriptors/memory. Every mutation is printed to stdout. Duplicate removal may not cover all overlap patterns. Help/build-flags return error status.

## Test Signals
Use fixture containers with partitioned logs, duplicates, corrupt blocks, and boundary versions; verify output decodes/restores and begin/end filtering is correct.
