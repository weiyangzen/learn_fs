# sources/distributed-fs/tahoe-lafs/src/allmydata/storage/shares.py

## Purpose
Provides a small dispatcher for opening a share file from disk without the caller already knowing whether it is mutable or immutable.

## Important APIs, Types, And Functions
`get_share_file(filename)` reads the first 32 bytes, uses `MutableShareFile.is_valid_header()` to recognize mutable containers, returns `MutableShareFile(filename)` for mutable shares, and otherwise returns an immutable `ShareFile(filename)`.

## Control Flow
The function performs a minimal header probe and then constructs the matching share object. Anything not recognized as mutable is assumed immutable, leaving immutable validation to `ShareFile`.

## State And Persistence
The module has no mutable state and writes nothing. Its only persistence effect is that it chooses the object that will later interpret the existing on-disk file.

## Dependencies And Integration Points
Depends on `allmydata.storage.mutable.MutableShareFile` and `allmydata.storage.immutable.ShareFile`. It is useful for tools or crawlers that need a generic share abstraction.

## Risks And Test Signals
The fallback-to-immutable behavior can surface malformed files as immutable parsing failures rather than an early unknown-type error. Tests should include valid mutable headers, valid immutable headers, truncated files, random files, and confirmation that mutable v1/v2 schemas are both recognized through the shared header logic.
