## sources/storage-engines/pebble/sstable/block/physical.go

Purpose: Builds, owns, writes, and recycles physical blocks: logical block bytes plus compression indicator/checksum trailer. It also provides temporary buffers used throughout block writing.

Important APIs/types/functions: `PhysicalBlock`, `TrailerLen`, `Trailer`, `MakeTrailer`, `PhysicalBlockLength`, `AlreadyEncodedPhysicalBlock`, `OwnedPhysicalBlock`, `WriteAndReleasePhysicalBlock`, `PhysicalBlockMaker`, `PhysicalBlockFlags`, `NoFlags`, `DontCompress`, `TempBuffer`, `NewTempBuffer`, and temp buffer methods.

Control flow: `PhysicalBlockMaker.Init` constructs a `Compressor` and initializes a `Checksummer`. `Make` obtains a `TempBuffer`, compresses unless `DontCompress`, records uncompressed stats if skipped, computes checksum over physical bytes plus compression indicator, appends trailer, and returns a releasable `PhysicalBlock`. `WriteAndReleasePhysicalBlock` writes `tb.Data()` to an `objstorage.Writable` and releases even on error. `Close` transfers compressor input-byte counts to counters and closes compressors.

State and persistence behavior: The trailer is exactly 5 bytes: one compression indicator byte followed by little-endian uint32 checksum. `PhysicalBlockLength.WithTrailer/WithoutTrailer` maintains trailer-aware sizes. `TempBuffer` instances are pooled and retained only if below `tempBufferMaxReusedSize`.

Dependencies and integration points: Used by SSTable/blob writers to serialize blocks. Depends on `objstorage.Writable`, `internal/invariants`, `encoding/binary`, `sync.Pool`, `slices`, `Compressor`, and `Checksummer`.

Risks: Callers must release or transfer ownership of physical blocks to avoid retaining pooled buffers. `TempBuffer.Release` does not put back large buffers, and after releasing a large buffer it leaves `tb.b` non-nil but does not reinsert into the pool, so callers must not reuse released buffers. Checksum type support is inherited from `Checksummer`.

Test signals: `compression_test.go` stresses temp buffer append/reset/release and physical block creation. Broader writer/reader tests validate durable compatibility.
