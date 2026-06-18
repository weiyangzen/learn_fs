# sources/object-store/minio/cmd/local-locker_gen_test.go

## Purpose

`local-locker_gen_test.go` is generated test and benchmark coverage for the MessagePack methods in `local-locker_gen.go`. It verifies that the generated code compiles, round-trips zero values, skips encoded messages, and provides benchmark baselines.

## Important Tests And Control Flow

For `localLockMap`, `lockRequesterInfo`, and `lockStats`, each `TestMarshalUnmarshal*` marshals a zero value, unmarshals it, checks no trailing bytes remain, and checks `msgp.Skip` consumes the message. Each `TestEncodeDecode*` stream-encodes to a `bytes.Buffer`, checks the `Msgsize` upper bound, decodes into a fresh value, and verifies reader `Skip`. Benchmarks cover marshaling to a new slice, appending into a reused slice, unmarshalling, stream encoding, and stream decoding.

The file depends on `bytes`, `testing`, and `tinylib/msgp`. It does not interact with real locks or grid transport.

## Risks And Test Signals

This is a generated sanity suite, not behavioral lock coverage. It does not exercise non-empty maps, multiple resources, read/write flags, owner matching, timestamp values, nullable versus non-null `LastCleanup`, or nondeterministic map ordering. Regeneration drift should be caught by compilation and these basic tests, while lock semantics are covered separately in `local-locker_test.go`.
