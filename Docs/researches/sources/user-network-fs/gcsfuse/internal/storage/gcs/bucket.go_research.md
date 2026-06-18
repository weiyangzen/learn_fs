# sources/user-network-fs/gcsfuse/internal/storage/gcs/bucket.go

## Purpose
This file defines the central storage abstraction for gcsfuse: the `gcs.Bucket` interface, related writer interface, request-id context key, and bucket capability model.

## Important APIs and Types
`PirloState` distinguishes non-Pirlo buckets from Pirlo buckets with rapid writes enabled or disabled. `BucketType` describes hierarchical namespace, zonal, and Pirlo state. `IsRapid` returns true for zonal or any Pirlo bucket; `RapidWritesEnabled` returns true for zonal or Pirlo rapid-enabled buckets. `Writer` abstracts GCS object writers with `Write`, `Close`, `Flush`, `ObjectName`, and `Attrs`. `Bucket` includes object read, multi-range download, create, chunk/appendable writer creation, upload finalization, flush, copy, compose, stat, list, update, delete, move, folder operations, and `GCSName`.

## Control Flow and Integration
The interface is purely contractual. Implementations in storage backends satisfy it, mocks use it for tests, and higher-level filesystem code consumes it without binding to a particular Google client transport. Methods accept `context.Context` for blocking operations and request structs from `request.go`. Object-returning operations use `Object`, `MinObject`, `ExtendedObjectAttributes`, `Listing`, and `Folder` from the same package.

## State, Persistence, and Risks
No state is stored in this file, but the interface documents persistence guarantees such as create visibility, read availability, and delete semantics. Compatibility risk is high: adding, removing, or changing methods requires updating production bucket handles, fake buckets, and both mock implementations. The rapid-write distinction drives client selection and writer behavior elsewhere, so misclassifying `BucketType` can select the wrong transport or upload semantics.
