# sources/object-store/minio/cmd/batch-expire_gen.go

Purpose: Generated msgp serialization for batch-expire job configuration types that are embedded in persisted `BatchJobRequest` values and possibly reused across job state handling.

Important APIs/types/functions: Provides `DecodeMsg`, `EncodeMsg`, `MarshalMsg`, `UnmarshalMsg`, and `Msgsize` for `BatchJobExpire`, `BatchJobExpireFilter`, and `BatchJobExpirePurge`. `BatchJobExpire` serializes API version, bucket, prefix, notification config, retry config, and rule list. `BatchJobExpireFilter` serializes older-than duration, optional created-before time, tags, metadata, size filter, type, name, and nested purge retain count. `BatchJobExpirePurge` serializes retain versions.

Control flow: Reader methods consume msgpack maps and skip unknown fields. Slice fields are resized or reused before decoding element structs. Optional `CreatedBefore` uses nil-aware decode/encode, allocating `time.Time` when present. Writer methods emit fixed map sizes and call nested generated methods for common types.

State/persistence behavior: This is the binary format for expire job definitions when `BatchJobRequest` is saved under `batch-jobs/<jobID>`. It excludes unexported YAML source-location fields, so line/column diagnostics are parse-time only and are not recoverable from persisted msgp.

Dependencies/integration: Depends on `time`, `tinylib/msgp`, `BatchJobPrefix`, `BatchJobNotification`, `BatchJobRetry`, `BatchJobKV`, `BatchJobSizeFilter`, and `xtime.Duration` generated methods. Used indirectly by `BatchJobRequest.MarshalMsg` and `UnmarshalMsg`.

Risks/test signals: Any structural change to expire YAML types requires regeneration. Unknown fields are skipped, which helps forward compatibility, but renamed fields or changed semantics can silently zero defaults. Generated tests exercise zero-value round trips and benchmarks for all three types; they do not validate non-empty rules, optional time pointers, or compatibility across releases.
