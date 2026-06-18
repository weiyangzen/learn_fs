# sources/user-network-fs/rclone/backend/chunker/chunker.go

## Purpose
`chunker.go` implements rclone's chunker backend, a wrapper filesystem that splits large logical files into multiple objects on an underlying remote and optionally stores a small metadata object at the logical file name.

## Important APIs, Types, And Control Flow
`NewFs` parses options, builds the wrapped remote, requires server-side move/copy capability, configures name format, metadata, hash mode, and transaction mode, then advertises masked features. `setChunkNameFormat`, `makeChunkName`, and `parseChunkName` define the data/control/temporary chunk naming contract. `List`/`processEntries` group chunks into `Object` wrappers while hiding temporary/control chunks. `NewObject` scans a directory to assemble one logical object. `put` uploads through `chunkingReader`, writes temporary chunk names, validates size, optionally finalizes small files as normal objects, renames chunks or records transaction ID, writes metadata, and rolls back on error. Object methods implement remove, server-side copy/move, open via `linearReader`, hash lookup from metadata or wrapped object, and metadata parsing/marshalling.

## State And Persistence
Persistent state lives entirely on the wrapped remote: data chunks, optional metadata object, and temporary transaction suffixes. In-memory state includes chunker options, regex/format strings, random transaction ID generator, object chunk slices, cached size, metadata hashes, `xactID`, and lazy metadata-read flags.

## Dependencies And Integration Points
Chunker integrates rclone core `fs`, `operations`, accounting wrappers, hash types, config parsing, path parsing, and optional wrapped features such as `Copy`, `Move`, `DirMove`, `ChangeNotify`, `PutStream`, metadata directories, cleanup, and quota. It wraps and unwraps FS/Object interfaces for stacked backends.

## Risks And Test Signals
Key risks are accidental exposure or mutation of chunk files, metadata version incompatibility, chunk number overflow, transaction ID collisions, orphan temp chunks after crashes, server-side copy/move partial failures, hash guarantees, and list performance because `NewObject` scans directories. Internal tests cover name parsing, corruption prevention, future metadata refusal, backwards compatibility between rename and norename transactions, server-side moves, small-file internals, metadata-like user input, chunk overflow, and hash-all behavior.
