# sources/object-store/rustfs/crates/protocols/src/swift/slo.rs

Provides Swift Static Large Object support: JSON manifests describe segment objects, the module validates those segments, stores a manifest side object, creates a marker object, streams assembled downloads, returns manifests, and deletes manifests plus segments.

Important API surface: `SLOSegment` models a segment path, size, etag, and optional range. `SLOManifest` owns ordered segments and optional creation time, with `from_json`, `total_size`, `calculate_etag`, and async `validate`. Request handlers are `handle_slo_put`, `handle_slo_get`, `handle_slo_get_manifest`, and `handle_slo_delete`. Helpers parse segment paths, detect SLO marker metadata, parse Range headers, calculate segment slices, generate transaction ids, and build a chained segment stream.

Control flow: PUT requires credentials, reads the full body, parses JSON, enforces a 2 MiB manifest limit after collection, validates each segment with `object::head_object`, stores `<object>.slo-manifest` with SLO metadata, then writes a zero-byte marker at the requested object path. GET loads the manifest side object, optionally parses a single Range header, computes segment ranges, builds an async stream that fetches each needed segment in order, and returns 200 or 206 with Swift SLO headers. Manifest GET returns raw JSON. DELETE loads the manifest, best-effort deletes every segment, then deletes manifest and marker.

Persistence is ordinary object storage: the JSON manifest side object and zero-byte marker object carry `x-swift-slo`, `x-slo-etag`, and `x-slo-size` metadata. Segment data remains in normal Swift/S3 objects. Dependencies include Swift `object` helpers, `Credentials`, `s3s::Body`, `http_body_util`, `tokio_util::io::ReaderStream`, `futures`, `md5`, `uuid`, and `HTTPRangeSpec`. The Swift handler dispatches multipart-manifest query operations and SLO reads/deletes here.

Risks: the manifest body is collected before the 2 MiB check. `SLOSegment.range` is parsed but not enforced. `parse_range_header` does not handle multi-range requests and can underflow if total size is zero. DELETE ignores segment deletion errors, and the `.slo-manifest` key convention can collide with user object names.

Tests cover segment path parsing, manifest size/etag math, range parsing, segment-range calculations, JSON parsing, quote stripping, and edge cases. Storage-integrated flows are not directly tested here.
