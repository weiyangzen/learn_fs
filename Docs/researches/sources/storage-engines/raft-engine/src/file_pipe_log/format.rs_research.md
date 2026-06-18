# sources/storage-engines/raft-engine/src/file_pipe_log/format.rs

## Purpose
Defines filesystem-level raft-engine log object names, reserved-file names, lock-file path, zero-padding detection, and encoded log file header format.

## Important APIs, Types, And Functions
Exports `is_zero_padded`, trait `FileNameExt` for `FileId`, `parse_reserved_file_name`, `build_reserved_file_name`, and `LogFileFormat`. Constants define 16-digit sequence width, append/rewrite/reserved suffixes, and the magic header.

## Control Flow
`FileId::parse_file_name` parses fixed-width sequence prefixes and suffixes into append or rewrite queue IDs. Builders format file names and paths. `LogFileFormat::encode` writes the magic header, version, and V2 alignment payload. `decode` validates the magic header, decodes the version, validates payload length, and decodes alignment when present.

## State And Persistence Behavior
The file format is persisted in every log file header. V1 headers carry no alignment payload; V2 carries alignment and supports log signing/recycling elsewhere. Reserved append files use a distinct suffix and contain zero padding before reuse.

## Dependencies And Integration Points
Depends on codec number encoders/decoders, `pipe_log::{FileId, FileSeq, LogQueue, Version}`, numeric enum conversion, and engine errors. File scanning, recovery, recycling, and lock management rely on these names and headers.

## Risks And Edge Cases
`is_zero_padded` only checks first and last bytes, so corrupt interior bytes may pass this early check and fail later processing. Header corruption, unknown versions, missing payload, and V1 nonzero alignment are important compatibility cases. Filename parsing ignores short or wrong-suffix files.

## Test Signals
Tests cover padding checks, append/rewrite filename parsing/building, version conversion, header encode/decode, abnormal versions, V1 alignment assertion, and log file context signatures.
