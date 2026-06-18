## sources/user-network-fs/gcsfuse/internal/util/sizeof_test.go

Purpose: Correctness tests for raw and nested size calculations.

Important APIs/types/functions: tests for `UnsafeSizeOf`, `contentSizeOfString`, `contentSizeOfArrayOfStrings`, `contentSizeOfStringToStringMap`, `contentSizeOfStringToStringArrayMap`, `contentSizeOfServerResponse`, `NestedSizeOfGcsMinObject`, and `NestedSizeOfGcsFolder`.

Control flow: expected sizes are computed from `unsafe.Sizeof`, known string lengths, and helper constants; tests compare helper results across empty and populated values.

State and persistence behavior: in-memory only.

Dependencies and integration points: covers `gcs.MinObject`, `gcs.Folder`, `googleapi.ServerResponse`, and `http.Header` map structures.

Risks: expected values mirror implementation conventions and do not prove real heap usage. Map iteration order does not matter because values are summed.

Test signals: strong guard against accidental arithmetic/schema changes in manual memory-estimation code.
