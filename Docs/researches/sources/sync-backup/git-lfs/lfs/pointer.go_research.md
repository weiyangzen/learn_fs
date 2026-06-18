# sources/sync-backup/git-lfs/lfs/pointer.go

Purpose: encodes and decodes Git LFS pointer files, including legacy version aliases and pointer extension metadata.

Important APIs/types/functions: `Pointer`, `PointerExtension`, `ByPriority`, `NewPointer`, `NewPointerExtension`, `Encode`, `Encoded`, `EmptyPointer`, `EncodePointer`, `DecodePointerFromBlob`, `DecodePointerFromFile`, `DecodePointer`, `DecodeFrom`, `verifyVersion`, `decodeKV`, `parseOid`, `parsePointerExtension`, `validatePointerExtensions`, and `decodeKVData`.

Control flow: encoding emits canonical version, extension lines, OID, and size, but returns an empty string for size zero. Decoding reads up to `blobSizeCutoff`, preserves a reader for the full original data on failure, rejects empty input as an empty pointer, parses ordered key/value lines, validates version aliases, OID type/hash, size, extension priority/name/OID, rejects duplicate priorities, sorts extensions, and marks canonical pointers by comparing encoded output to input.

State/persistence behavior: file/blob decoders read from disk or object streams and enforce regular-file and size-cutoff checks. No writes except through encode writer.

Dependencies/integration: central to clean/smudge filters and all scanners. Depends on Git LFS errors, filesystem empty object SHA, and `gitobj.Blob`.

Risks/test signals: parser requires strict key order except extension lines; extra lines and bad keys become not-a-pointer or bad-pointer errors. `Encoded` returning empty for zero-size pointers is an important special case. Extension key regex only allows one digit of priority, while parser later accepts nonnegative integer after splitting, so high priorities may be rejected at key validation.
