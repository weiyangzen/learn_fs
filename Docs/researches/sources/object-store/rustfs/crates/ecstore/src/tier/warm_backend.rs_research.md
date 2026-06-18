# sources/object-store/rustfs/crates/ecstore/src/tier/warm_backend.rs

## Purpose

Defines the common warm-tier backend trait, metadata promotion into put options, backend probing, and provider factory.

## Important APIs and Types

`WarmBackendImpl` is a boxed async trait object. `WarmBackendGetOpts` carries range settings. `WarmBackend` defines `put`, `put_with_meta`, `get`, `remove`, and `in_use`. `build_transition_put_options`, `check_warm_backend`, and `new_warm_backend` are the main functions.

## Control Flow

`build_transition_put_options` promotes content/cache/expires/object-lock headers into `PutObjectOptions`, parses timestamps as RFC3339/RFC2822, removes promoted headers from user metadata, and returns remaining metadata. `check_warm_backend` writes, reads, and removes a fixed probe object. `new_warm_backend` switches on `TierType` and constructs S3, RustFS, MinIO, Aliyun, Tencent, Huawei Cloud, Azure, GCS, or R2 backends.

## State and Persistence Behavior

No local persistence. Probing mutates remote state by putting/removing `probeobject`.

## Dependencies and Integration Points

Integrates tier config DTOs, provider modules, admin errors, transition API readers/options, S3 object-lock DTOs, RustFS header helpers, bytes, time parsing, and tracing.

## Risks and Edge Cases

The `probe` parameter in `new_warm_backend` is unused in visible code. Probe failures are mostly mapped to permission errors. Fixed probe object name can collide if backend prefixes are not isolated. Header behavior depends on canonical lookup/removal.

## Test Signals

Tests cover metadata promotion, object-lock retention/legal-hold/mode preservation, and removal of promoted headers from user metadata.
