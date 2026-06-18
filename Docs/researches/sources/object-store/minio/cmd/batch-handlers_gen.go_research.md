# sources/object-store/minio/cmd/batch-handlers_gen.go

Purpose: Generated msgp serialization for batch handler types: `BatchJobPrefix`, `BatchJobRequest`, and durable `batchJobInfo`.

Important APIs/types/functions: `BatchJobPrefix` serializes as a string array. `BatchJobRequest` serializes ID, user, started time, and nullable nested `Replicate`, `KeyRotate`, and `Expire` request pointers. `batchJobInfo` serializes compact keyed progress fields: version (`v`), job ID/type, start/last update, retry/attempt counts, complete/failed flags, last bucket/object, object/delete-marker success/failure counts, and byte counters.

Control flow: Decode/unmarshal paths use map-key switches and skip unknown fields. Request decoding allocates nested job structs when a non-nil value is present. Prefix decoding resizes the slice directly from an array header. `batchJobInfo` uses short msgp keys to reduce report size, while `BatchJobRequest` uses descriptive keys.

State/persistence behavior: This file defines the binary layout for persisted job requests and job reports. It must match the 4-byte format/version framing implemented by `batchJobInfo.updateAfter` and `loadByPath`; the frame is not handled here, only the body.

Dependencies/integration: Depends on `tinylib/msgp` and generated methods for nested replicate/key-rotation/expire types. Called by `BatchJobRequest.save/load`, `batchJobInfo.updateAfter/loadByPath`, and generated tests.

Risks/test signals: Adding a new batch job type or changing report counters requires regenerating this file and checking backward compatibility. Unknown field skipping helps additive changes, but missing fields decode to zero, which can affect resume and status output. Generated tests cover zero-value round trips and benchmarks for prefix, request, and info.
