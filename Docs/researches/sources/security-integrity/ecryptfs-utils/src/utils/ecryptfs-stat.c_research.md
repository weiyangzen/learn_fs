<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs-stat.c -->
# sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs-stat.c

Final split target: `Docs/researches/sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs-stat.c_research.md`. Source lines read for this pass: 75.

## Purpose
User utility that prints eCryptfs metadata/stat information for a supplied file using libecryptfs helpers.

## Important APIs, Types, And Functions
Defines `usage` and `main`; uses `struct ecryptfs_crypt_stat_user` and `ecryptfs_parse_stat` from the eCryptfs headers/library.

## Control Flow
Validates one filename argument, opens it read-only, reads up to 4096 bytes, parses eCryptfs metadata from that buffer, and prints file version, decrypted size, header bytes, metadata location, encrypted/plaintext flag, and HMAC flag.

## State And Persistence Behavior
Read-only against the target file; output is diagnostic text.

## Dependencies And Integration Points
Depends on `src/libecryptfs/libecryptfs.la`, generated config, stdio, and file metadata/header bytes that exist on eCryptfs encrypted files.

## Risks And Edge Cases
Behavior depends on whether the input includes readable eCryptfs metadata in the first page. Parse failure is reported as 'metadata not found' but returns success after printing the message.

## Test Signals
Use encrypted and plaintext/non-eCryptfs files to verify parsed metadata fields and graceful metadata-not-found behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs-stat.c -->
