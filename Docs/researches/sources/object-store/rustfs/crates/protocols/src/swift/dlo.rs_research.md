# sources/object-store/rustfs/crates/protocols/src/swift/dlo.rs

## Purpose
`dlo.rs` implements Swift Dynamic Large Object support. A DLO manifest object is a zero-byte marker with `x-object-manifest` metadata whose value is `container/prefix`; downloads discover matching segment objects at request time, sort them lexicographically, and stream them as one logical object.

## Important APIs, Types, And Functions
`ObjectInfo` is the local segment listing shape with name, size, content type, and etag. `is_dlo_object` detects manifests by `object::head_object`. `list_dlo_segments` delegates prefix listing to `container::list_objects` and sorts by object name. `handle_dlo_get` parses the manifest, lists segments, computes total size, handles optional Range, builds Swift response headers, and streams segment bodies. `handle_dlo_register` validates the manifest and stores marker metadata via `object::put_object_with_metadata`. Private helpers include `parse_dlo_manifest`, `parse_range_header`, `calculate_dlo_segments_for_range`, `create_dlo_stream`, and UUID-based `generate_trans_id`.

## Control Flow
GET flow is metadata detection in `handler.rs`, parse `container/prefix`, list segment container, compute total size, select full or partial segment byte spans, then lazily call `object::get_object` per segment and flatten `ReaderStream`s into one response body. PUT registration flow is triggered by `X-Object-Manifest`, creates marker metadata, and returns `201 Created`.

## State, Persistence, And Dependencies
DLO state is persisted only as object user metadata plus the segment objects already stored in Swift/S3-backed buckets. Segment enumeration depends on the container listing module, while segment reads and marker writes depend on the object module and RustFS credentials. The DLO code itself holds no durable local state.

## Integration Points
`handler.rs` calls `is_dlo_object` and `handle_dlo_get` for regular and symlink-resolved object reads, and calls `handle_dlo_register` for PUTs with `x-object-manifest`. It shares range behavior with `object.rs` and handler-local parsing, and returns `x-object-manifest`, `x-trans-id`, and `x-openstack-request-id` headers.

## Risks And Test Signals
Range parsing is duplicated here and in other Swift modules, so edge cases may diverge. `parse_range_header` can underflow for zero total size because it computes `total_size - 1`; current DLO GET rejects empty segment sets but not zero-byte segment totals. Large DLOs require full segment listing before streaming, and missing segments are discovered only when streaming reaches them. Unit tests cover manifest parsing, range parsing, segment span calculation, transaction ID shape, and `ObjectInfo`; no integration test verifies real object-store streaming or manifest lifecycle.
