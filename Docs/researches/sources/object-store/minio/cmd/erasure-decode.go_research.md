# sources/object-store/minio/cmd/erasure-decode.go

Purpose: Implements erasure-coded object reads and shard repair reads. It reads shards in parallel, reconstructs missing data, supports ranged reads, and heals missing/corrupt shards by reconstructing full data/parity blocks.

Important APIs/types/functions: `parallelReader` tracks `io.ReaderAt` sources, original reader positions, shard offsets/sizes, per-disk buffers, preferred-reader remapping, and pooled stash buffers. `newParallelReader` initializes shard offsets and optionally slices a global byte pool. `preferReaders` moves preferred disks earlier while preserving output buffer mapping. `Read` launches enough concurrent reads to satisfy data-block quorum, retries alternate readers on nil/error readers, marks original readers nil on failure, and returns reconstructable buffers plus expected heal signals (`errFileNotFound` or `errFileCorrupt`). `Erasure.Decode` validates range arguments, iterates erasure blocks, reconstructs data blocks, writes requested subranges with `writeDataBlocks`, and returns a deferred heal signal when data was readable but some source shard was missing/corrupt. `Erasure.Heal` reconstructs data and parity blocks and writes them through `multiWriter`.

Control flow and state: Reads are block-oriented. For each erasure block, `parallelReader.Read` advances shard offset only if enough shards are available to decode. `Decode` calculates block-relative offsets for first/middle/last blocks and checks the final written byte count. `Heal` walks all blocks from zero to object length and writes reconstructed shards to supplied writers with write quorum 1.

Dependencies and integration points: Uses bitrot reader implementations through `io.ReaderAt`, global byte-pool capacity, `writeDataBlocks`, `multiWriter`, erasure math from `erasure-coding.go`, and MinIO error values. Healing code calls `Erasure.Heal` after it builds bitrot readers/writers for specific object parts.

Risks: Concurrency is coordinated through a buffered trigger channel and goroutines; incorrect reader-to-buffer mapping would corrupt shard positions. Returned `errFileNotFound`/`errFileCorrupt` can be non-fatal and signal a heal need, so callers must not treat every non-nil decode error the same. Range math around block boundaries and last shard size is fragile.

Test signals: Decode tests cover many data/parity/offline combinations, range offsets/lengths, quorum failures, invalid arguments, random ranges, and benchmarks.
