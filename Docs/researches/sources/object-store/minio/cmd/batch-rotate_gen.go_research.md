# sources/object-store/minio/cmd/batch-rotate_gen.go

This generated `tinylib/msgp` file serializes the batch key-rotation job model. It implements the standard msgp methods for `BatchJobKeyRotateEncryption`, `BatchJobKeyRotateFlags`, `BatchJobKeyRotateV1`, `BatchKeyRotateFilter`, `BatchKeyRotateNotification`, and `BatchKeyRotationType`.

The persisted schema uses map keys `Type`, `Key`, `Context`, `Filter`, `Notify`, `Retry`, `APIVersion`, `Flags`, `Bucket`, `Prefix`, `Encryption`, `NewerThan`, `OlderThan`, `CreatedAfter`, `CreatedBefore`, `Tags`, `Metadata`, `KMSKeyID`, `Endpoint`, and `Token`. `BatchKeyRotationType` is encoded as a string. The unexported `kmsContext` field in `BatchJobKeyRotateEncryption` is ignored by the source annotation, so only the user-supplied base64 context string persists; runtime validation reconstructs the derived context.

Control flow mirrors msgp output: decoders read map headers and switch on field names, skip unknown fields, allocate/reuse slices for tag and metadata filters, and delegate nested types where available. Encoders write fixed map sizes and field names in generated order. `Msgsize` methods provide upper-bound estimates used by append benchmarks and callers that preallocate buffers.

The state impact is high because batch rotation jobs can be persisted/resumed. If source structs change without rerunning msgp generation, persisted job definitions may silently drop new fields or decode old fields incorrectly. Unknown-field skipping supports forward compatibility for extra fields but not type changes. The generated code also serializes notification tokens and key identifiers, so storage and logs around these payloads should be treated as sensitive.

Dependencies are the msgp runtime and the batch rotation model from `batch-rotate.go`. Test signals come from `batch-rotate_gen_test.go`, which validates zero-value round trips and skip behavior. Semantic coverage for non-zero encryption contexts, filters, retry settings, and KMS-key values is absent.
