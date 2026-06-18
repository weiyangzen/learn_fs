# File Research: sources/windows/reactos/drivers/filesystems/btrfs/zstd/zstd_ddict.h

## Summary
Declares internal DDict helpers not already exposed through `zstd.h`.

## Key APIs
- `ZSTD_DDict_dictContent()`.
- `ZSTD_DDict_dictSize()`.
- `ZSTD_copyDDictParameters()`.

## Important Behavior
The header bridges public DDict APIs from `zstd.h` with decompression internals that need direct access to dictionary bytes, dictionary size, and preloaded entropy tables.

## Risks
The helper functions assume non-null DDict pointers in their implementation. Callers must keep DDict lifetime rules consistent with copied versus referenced dictionary storage.
