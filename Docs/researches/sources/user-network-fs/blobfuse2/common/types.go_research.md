# sources/user-network-fs/blobfuse2/common/types.go
## sources/user-network-fs/blobfuse2/common/types.go

Purpose: defines common constants, log-level enum, logging config, block metadata structures, block-list helpers, UUID/block-id helpers, and default path initialization.

Important APIs/types/functions: version/default constants, `FuseIgnoredFlags`, `Blobfuse2Version`, `DefaultWorkDir`, `LogLevel` and `ELogLevel`, `LogConfig`, block flags, `Block`, `Dirty`, `Truncated`, `BlockOffsetList`, `BinarySearch`, `FindBlocks`, `FindBlocksToModify`, `uuid`, `NewUUIDWithLength`, `NewUUID`, `GetBlockID`, `GetIdLength`, and `azureSpecialContainers`.

Control flow: log levels are enum-style methods over `LogLevel` with string parsing through `github.com/JeffreyRichter/enum`. Block helpers search sorted block ranges, mark dirty blocks that overlap write ranges, report append-only and larger-than-file cases, and validate file size against the last block end. UUID helpers generate random bytes and set RFC4122 version/variant bits before base64 encoding block IDs. `init` derives default work/log/stats paths from `$HOME` or `./`.

State and persistence: package globals hold version, default paths, monitoring flags, pipes, and mount path. Block helpers mutate block flags. No direct persistence.

Dependencies/integration: used broadly by logging, config, cache, mount, storage, and utility code.

Risks: `FindBlocks` and `FindBlocksToModify` assume sorted non-overlapping blocks. `FindBlocksToModify` can panic on empty `BlockList` when a found path later references the last element, though no-found append case returns earlier. `Blobfuse2Version` is mutable, which aids tests but can affect runtime if changed. Random UUID errors are ignored.

Test signals: `types_test.go` covers binary search, block modification calculations, append-only detection, and default path initialization.
