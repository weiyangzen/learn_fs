# sources/security-integrity/gocryptfs/internal/contentenc/file_header.go

Purpose: This file defines the per-file content header format used to bind encrypted blocks to a random file ID.

Important APIs and types: Constants define header version, ID length, and total header length. `FileHeader` stores version and ID. `Pack` serializes the header, `ParseHeader` validates and parses bytes, and `RandomHeader` creates a new header with random ID.

Control flow and state: Nonempty encrypted files persist the header before content blocks. Parsing rejects wrong lengths, unsupported versions, all-zero IDs, and all-zero headers where appropriate.

Dependencies and integration points: File IDs feed `content.go` associated data, preventing block swapping across files. Used by file I/O and fsck.

Risks and test signals: Header corruption must be detected cleanly. Risks include accepting zero IDs or version mismatch. Signals are parse/pack round trips, random ID length, and rejection tests for malformed headers.
