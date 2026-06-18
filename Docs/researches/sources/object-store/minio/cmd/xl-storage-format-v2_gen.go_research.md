# sources/object-store/minio/cmd/xl-storage-format-v2_gen.go

## Purpose
This generated file supplies `tinylib/msgp` encoders, decoders, marshalers, unmarshalers, and `Msgsize` estimates for the XL metadata v2 enum and record types defined in `xl-storage-format-v2.go`. It is part of the durable on-disk wire contract for MinIO object metadata and should be regenerated from source annotations rather than hand-edited.

## Important APIs, Types, and Functions
The scalar enum codecs cover `ChecksumAlgo`, `ErasureAlgo`, `VersionType`, and `xlFlags` as single `uint8` values. `xlMetaBuf` is encoded as raw bytes. `xlMetaDataDirDecoder` is a shallow map decoder for only `V2Obj.DDir`; `SharedDataDirCount` uses it to avoid full object unmarshalling when checking data-dir sharing.

The main codecs are for `xlMetaV2DeleteMarker`, `xlMetaV2Object`, `xlMetaV2Version`, and tuple-style `xlMetaV2VersionHeader`. Delete markers encode fields `ID`, `MTime`, and optional `MetaSys`. Object versions encode all erasure fields, part arrays, size/modtime, optional `PartIdx`, and allownil `PartETags`, `PartASizes`, `MetaSys`, and `MetaUsr`. `xlMetaV2Version` encodes `Type`, optional `V1Obj`, optional `V2Obj`, optional `DelObj`, and writer version `v`. The header is encoded as a fixed array of seven values, making the tuple arity a compatibility boundary.

## Control Flow
Each decode path reads a map or array header, switches on msgp field names, fills the target struct, skips unknown fields, and clears omitted pointer/slice/map fields according to the generated clear-omitted behavior. Encode/marshal paths compute omitted-field masks, write map headers sized to the emitted fields, then serialize fields in generated order. Unmarshal paths return the unused suffix so callers can verify no trailing bytes remain or compose decoders. `Msgsize` functions provide upper-bound allocation sizing for `msgp.Require` and benchmark allocation control.

## State and Persistence Behavior
The field names in this file are the persisted schema names used in `xl.meta`: short tags like `ID`, `DDir`, `EcM`, `EcN`, `PartIdx`, `MetaSys`, `MetaUsr`, `DelObj`, and `v`. Unknown fields are skipped, supporting forward compatibility, while missing omitted fields are cleared to avoid stale data when reusing structs. The tuple header requires exactly seven elements, so any header shape change requires coordinated version handling in `xl-storage-format-v2-legacy.go` and `decodeXLHeaders`.

## Dependencies and Integration Points
The file depends on `github.com/tinylib/msgp/msgp` and the hand-written types from the same package. It is invoked by `xlMetaV2.AppendTo`, `loadIndexed`, `loadLegacy`, `getIdx`, `setIdx`, signature generation, compatibility repairs, `xlMetaBuf` readers, and tests. It also delegates legacy object codec work to `xlMetaV1Object` methods generated elsewhere.

## Risks and Edge Cases
The biggest risk is drift between source struct tags and generated output. Manual edits would be overwritten and can silently change disk encoding. Changing allownil/omitempty tags affects nil-vs-empty normalization and signatures. `xlMetaV2VersionHeader` has strict array-size validation, so adding fields without versioned unmarshal support will reject existing/new metadata. Map iteration order is not deterministic, but higher-level signature code hashes maps separately and removes maps before marshaling when deterministic signatures are required.

## Test Signals
`xl-storage-format-v2_gen_test.go` verifies generated marshal/unmarshal and encode/decode/skip paths for the main metadata structs and provides allocation/throughput benchmarks. Broader integration is exercised by v2 metadata load/append/merge tests, which would fail if generated codecs stopped preserving fields or changed tuple/map behavior unexpectedly.
