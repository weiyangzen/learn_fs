
# sources/sync-backup/restic/internal/repository/pack/packedblob.go

Purpose: adapts internal pack blob metadata to the public `restic.PackBlob` interface used by repository, prune, and index consumers.

`PackedBlob` combines a pack ID with a `Blob`. Methods expose `PackID`, `Handle`, `CiphertextLength`, `UncompressedCiphertextLength`, `PlaintextLength`, and `IsCompressed`. The compile-time assertion ensures interface conformance.

There is no direct persistence here; it is a view over index entries and pack headers. Integration points include `Repository.LookupBlob`, `Repository.ListBlobs`, `pack.Size`, prune statistics, and associated blob sets. Risks are mainly semantic: consumers intentionally do not see blob offsets through `restic.PackBlob`, which prevents leaking pack internals but means offset-sensitive code must use `pack.Blob` internally.
