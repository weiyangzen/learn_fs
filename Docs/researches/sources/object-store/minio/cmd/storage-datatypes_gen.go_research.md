# sources/object-store/minio/cmd/storage-datatypes_gen.go

## Purpose

`storage-datatypes_gen.go` is generated `tinylib/msgp` serialization code for MinIO storage datatypes and storage REST/grid request and response envelopes. It gives the storage layer zero-reflection MessagePack encoders, decoders, byte marshalers, byte unmarshalers, and size estimators for the wire-facing types declared primarily in `storage-datatypes.go`.

The file is on the critical storage compatibility path. Types such as `DiskInfo`, `FileInfo`, `FileInfoVersions`, `VolInfo`, and `VolsInfo` carry disk metadata, object metadata, erasure metadata, inline object data, version listings, and volume information across internode RPC boundaries and sometimes represent persisted metadata formats. Handler parameter structs such as `DeleteVersionHandlerParams`, `ReadMultipleReq`, `RenameDataHandlerParams`, and `WriteAllHandlerParams` encode storage REST/grid calls compactly.

## Important APIs, Types, And Functions

Every generated type implements the same five-method msgp surface: `DecodeMsg(*msgp.Reader) error`, `EncodeMsg(*msgp.Writer) error`, `MarshalMsg([]byte) ([]byte, error)`, `UnmarshalMsg([]byte) ([]byte, error)`, and `Msgsize() int`.

The generated surface covers `BaseOptions`, `CheckPartsHandlerParams`, `CheckPartsResp`, `DeleteBulkReq`, `DeleteFileHandlerParams`, `DeleteOptions`, `DeleteVersionHandlerParams`, `DeleteVersionsErrsResp`, `DiskInfo`, `DiskInfoOptions`, `DiskMetrics`, `FileInfo`, `FileInfoVersions`, `FilesInfo`, `ListDirResult`, `LocalDiskIDs`, `MetadataHandlerParams`, `RawFileInfo`, `ReadAllHandlerParams`, `ReadMultipleReq`, `ReadMultipleResp`, `ReadPartsReq`, `ReadPartsResp`, `RenameDataHandlerParams`, `RenameDataInlineHandlerParams`, `RenameDataResp`, `RenameFileHandlerParams`, `RenameOptions`, `RenamePartHandlerParams`, `UpdateMetadataOpts`, `VolInfo`, `VolsInfo`, and `WriteAllHandlerParams`.

Tuple-encoded types use fixed arrays and strict arity checks. `DiskInfo` requires an 18-element array, `FileInfo` requires a 28-element array, `FileInfoVersions` requires a 5-element array, `VolInfo` requires a 3-element array, and each `VolsInfo` element is a 3-element `VolInfo` tuple. These checks make field additions, removals, or reordering wire-incompatible unless coordinated with an internode/storage metadata version bump.

Map-encoded request/response envelopes use compact `msg` tags and skip unknown fields. Examples include `ReadMultipleReq` keys `bk`, `pr`, `fl`, `ms`, `mo`, `ab`, and `mr`; `ReadMultipleResp` keys `bk`, `pr`, `fl`, `ex`, `er`, `d`, and `m`; `RenameDataHandlerParams` keys `id`, `sv`, `sp`, `dv`, `dp`, `fi`, and `ro`; and `MetadataHandlerParams` keys `id`, `v`, `ov`, `fp`, `uo`, and `fi`.

## Control Flow

Each decoder reads a map or array header, loops fields or tuple positions, decodes typed values, and wraps failures with field/index context via `msgp.WrapError`. Unknown map keys are consumed with `Skip`, which permits forward-compatible request maps where absent fields fall back to zero values. Tuple decoders instead reject arity mismatches with `msgp.ArrayError`, intentionally preventing silent compatibility drift for storage metadata objects.

Marshal paths preallocate with `msgp.Require(b, z.Msgsize())`, append a header, then append scalar fields and nested messages in deterministic struct order. Stream encoders write directly to `msgp.Writer`; byte unmarshalers return the remaining unconsumed bytes so callers and tests can detect trailing data. Slice decoders reuse existing capacity when possible; map decoders allocate on nil and call `clear` before repopulating an existing map, preventing stale keys when an instance is reused.

The generated `msgp:clearomitted` behavior is visible in omitted fields such as `ReadMultipleReq.Prefix` and `ReadMultipleResp.Prefix`/`Error`: decode paths track whether the field was present and explicitly reset omitted values to `""`. This matters when reusing structs from pools or across repeated decode calls.

## State And Persistence Behavior

The file does not perform disk I/O itself, but it defines the serialized shape of storage state and requests. `FileInfo` carries object metadata, erasure layout, replication state, inline data, checksum, version counters, and deletion flags. `RawFileInfo.Buf`, `FileInfo.Data`, and `FileInfo.Checksum` preserve nil-vs-empty byte-slice semantics where the original type requested `allownil`; decoders set nil for encoded nil and normalize non-nil byte reads to empty slices when needed.

`DiskMetrics` encodes maps of API latency accumulators and call counts plus aggregate availability, timeout, write, and delete counters. `RenameDataResp` carries a signature and an old data directory for the storage layer's two-phase rename cleanup. `CheckPartsResp` serializes integer status codes whose order is documented in `storage-datatypes.go` as data-loss-sensitive for mixed-version clusters.

## Dependencies And Integration Points

The only direct dependency is `github.com/tinylib/msgp/msgp`; nested generated calls integrate with msgp implementations on related MinIO types including `AccElem`, `ObjectPartInfo`, `ErasureInfo`, and `ReplicationState`. The generated handlers are consumed by storage REST/grid code around `StorageAPI` operations such as delete, rename, read, write, metadata update, disk info, read-multiple, and part verification.

The file is regenerated from `storage-datatypes.go` via `go:generate msgp -file=$GOFILE`; manual edits should not be made. Compatibility changes must be coordinated with comments in the hand-written datatype file that call out internode version bumps for metadata-bearing structures.

## Risks

The largest risk is wire incompatibility. Tuple arity changes fail hard, while map field tag changes silently change the protocol. `Msgsize()` is an upper-bound estimate; if it becomes too small, msgp will still grow buffers, but benchmarks and allocation assumptions can degrade. Reuse of slices and maps improves performance but means omitted-field clearing and nil handling are important for correctness.

Large encoded payloads can be carried in `FileInfo.Data`, `RawFileInfo.Buf`, `ReadMultipleResp.Data`, and `WriteAllHandlerParams.Buf`; callers must enforce size limits outside this file. Unknown fields are skipped in maps, so new optional fields are easier to roll out than tuple fields, but old nodes will discard them.

## Test Signals

`storage-datatypes_gen_test.go` exercises generated marshal/unmarshal and encode/decode paths for every generated type, verifies no trailing bytes remain, checks that `msgp.Skip` can skip encoded objects, warns on inaccurate `Msgsize`, and provides encode/decode/marshal benchmarks. `storage-datatypes_test.go` adds performance comparisons between msgp and gob for representative `VolInfo`, `DiskInfo`, and metadata-heavy `FileInfo` values.
