# sources/user-network-fs/gcsfuse/internal/storage/gcs/object.go

## Purpose
This file defines gcsfuse's internal object metadata models: full `Object`, compact `MinObject`, and `ExtendedObjectAttributes`.

## Important APIs and State
`ContentEncodingGzip` is the canonical gzip content-encoding string. `Object` represents a full GCS object generation with content headers, owner, size, encoding, checksums, media link, metadata, generation, metageneration, storage class, timestamps, component count, content disposition, custom time, event hold, and ACLs. `MinObject` carries the smaller attribute set used in list/stat paths. `ExtendedObjectAttributes` carries the fields omitted from `MinObject`. `Object.IsUnfinalized` and `MinObject.IsUnfinalized` return true when `Finalized` is zero. `MinObject.HasContentEncodingGzip` checks exact gzip encoding.

## Control Flow and Integration
The file contains simple data types and predicates. It integrates with request/response conversion, bucket operations, storage utilities, tests, and higher filesystem logic that needs generation, checksum, gzip, and finalized-state information. The component-count comment documents a deliberate local synthesis: objects without a GCS component count are treated as component count one.

## Risks and Test Signals
Exact string comparison means `GZIP` is not treated as gzip. Zero `Finalized` means unfinalized, which is important for rapid/appendable object paths. Splitting stat results between `MinObject` and `ExtendedObjectAttributes` requires conversion helpers to keep fields aligned.
