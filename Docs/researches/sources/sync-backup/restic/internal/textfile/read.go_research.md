<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/textfile/read.go -->
# sources/sync-backup/restic/internal/textfile/read.go

## Purpose
Reads text files while normalizing byte-order marks and UTF-16 encodings to UTF-8 bytes.

## Important APIs and Control Flow
`Decode` detects UTF-16 BOMs and decodes little/big endian content; `Read` loads a file then decodes it. Control flow checks known BOM prefixes, transforms with unicode decoders when needed, and returns original data when no BOM is present.

## State, Persistence, Dependencies, and Integration
State is transient byte slices. Dependencies include text encoding packages and `os.ReadFile`; integration is with config/list files that may come from Windows editors.

## Risks and Test Signals
Risks are unsupported encodings and malformed UTF-16 handling. Tests cover plain UTF-8, BOM variants, invalid data, empty files, and file read behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/textfile/read.go -->
