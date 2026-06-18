# sources/user-network-fs/rclone/lib/encoder/filename/fuzz.go

Source read signal: reviewed complete local file (35 lines, sha256 a5baec8b589a850b).

Purpose: Provides a go-fuzz harness for the filename encoder/decoder round trip and decoder robustness.

Important APIs/types/functions: The build-tagged `Fuzz(data []byte) int` function calls `Decode` on arbitrary data, then `Encode` and `Decode` on the original byte string.

Control flow: It first attempts to decode arbitrary bytes as a string and ignores result/errors to catch panics. It then encodes the input, decodes the encoded form, and panics if decoding fails or if bytes differ from the original input.

State and persistence behavior: No durable state is used. It exercises shared table initialization and table scratch under fuzz workload.

Dependencies and integration points: Uses `bytes` and `fmt` plus package functions. The `gofuzz` build tag keeps it out of normal builds and documents the `go-fuzz-build` invocation.

Risks and test signals: Strong signal for panic safety and reversibility over invalid UTF-8 byte strings. It does not assert minimal encoded size or distinguish expected corruption errors from unsupported/future table ids.
