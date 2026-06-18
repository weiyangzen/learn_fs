# sources/storage-engines/tikv/components/sst_importer/src/errors.rs

Purpose: unified importer error type, metric labeling, protobuf conversion, and error-code mapping.

Important APIs and types: `Error` covers IO, gRPC, UUID, future cancellation, RocksDB string errors, engine traits, parse int, file existence/corruption/path/chunk, boxed engine errors, external storage read errors, wrong key prefix, bad format, encryption, codec, file conflict, TTL/API/key-mode/resource/suspension/disk/mismatch/wrapper cases. `Result<T>` aliases this error. `error_inc` maps selected variants to `IMPORTER_ERROR_VEC` labels. `invalid_key_mode` formats invalid keys in uppercase hex. `From<Error> for import_sstpb::Error` produces gRPC response errors, including server-is-busy backoff for resource/suspension cases. `ErrorCodeExt` maps each variant to `error_code::sst_importer`.

Control flow: callers construct specific errors, optionally increment metrics with operation type, and gRPC service code can convert into protobuf errors. Error-code mapping delegates nested engine/encryption/codec mappings where available.

State and persistence behavior: increments Prometheus counters only. No persistence.

Dependencies and integration points: used throughout SST importer crate and exported from `lib.rs`. Integrates `error_code`, `kvproto`, `grpcio`, `encryption`, `engine_traits`, `tikv_util::codec`, and importer metrics.

Risks: `error_inc` intentionally ignores variants not in its match, so new errors may lack metrics unless added. Typo `RESOURCE_NOT_ENOUTH` is in the existing error-code constant and must stay aligned. Protobuf conversion loses detailed structured fields for most variants.

Test signals: no direct tests in this file; behavior is exercised by importer service tests and error-code tests elsewhere.
