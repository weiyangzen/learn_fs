# sources/object-store/minio/cmd/storage-rest-common_gen_test.go

Purpose: generated tests and benchmarks for msgp serialization of storage REST namespace scanner payloads.

Important APIs/types/functions: `TestMarshalUnmarshalnsScannerOptions`, `TestEncodeDecodensScannerOptions`, `TestMarshalUnmarshalnsScannerResp`, and `TestEncodeDecodensScannerResp` exercise byte-slice and stream-based round trips. Benchmarks cover marshal, append-style marshal, unmarshal, encode, and decode for both structs.

Control flow: tests instantiate zero-value structs, marshal them, unmarshal and ensure no trailing bytes remain, verify `msgp.Skip` consumes the entire encoded value, and stream encode/decode through a `bytes.Buffer`. Benchmarks use zero values and `msgp.NewEndlessReader` for decode throughput measurements.

State and persistence behavior: all state is in memory. No scanner or disk state is constructed.

Dependencies/integration: depends on `testing`, `bytes`, and `github.com/tinylib/msgp/msgp`. It guards the generated code used by `storageNSScannerRPC`.

Risks/test signals: useful for detecting stale or syntactically broken generated msgp code, but narrow because only zero values are tested. It will not catch nested `dataUsageCache` compatibility issues, scanner update/final sequencing errors, or server-side nil-cache validation regressions.
