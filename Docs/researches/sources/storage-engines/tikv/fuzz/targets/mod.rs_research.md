# sources/storage-engines/tikv/fuzz/targets/mod.rs

## Purpose
Holds the concrete fuzz target functions for TiKV utility codecs and TiDB query datatype codecs. The file is also a discovery source for `fuzz/cli.rs`, so public functions named `fuzz_*` are the target registry.

## Important APIs, Types, and Functions
Targets include `fuzz_codec_bytes`, `fuzz_codec_number`, decimal arithmetic/hash targets, time parse/from-packed targets, duration parse/from-nanos targets, and row v2 binary-search coverage. Helper traits map raw bytes into decimal round modes and time types. `fuzz_time` and `fuzz_duration` centralize conversion and operation coverage.

## Control Flow
Targets consume byte slices via `Cursor` and `ReadLiteralExt`, decode primitive values, construct codec/domain values, and invoke encode/decode/arithmetic/format/convert operations. Many operations intentionally ignore ordinary `Result`s so fuzzing focuses on panics, invariant violations, and sanitizer failures. Some targets require enough input bytes and return early through `?` on short or invalid data.

## State and Persistence Behavior
No persistent state. Each fuzz invocation allocates local cursors, buffers, contexts, and datatype values. Time targets create `EvalContext` values with fuzzed time zones.

## Dependencies and Integration Points
Depends on `tikv_util::codec`, `tidb_query_datatype` decimal/time/duration/row codecs, `anyhow`, and `util::ReadLiteralExt`. Imported by AFL/Honggfuzz/libFuzzer generated harnesses.

## Risks
Native-endian byte interpretation can reduce cross-platform corpus portability. Ignoring `Result` is intentional but may hide semantic correctness bugs that are not panics. The discovery regex depends on public function formatting. Some operations such as division/modulo and decimal conversion need careful panic-safety coverage.

## Test Signals
Run all discovered targets under at least one fuzzer for smoke coverage. Unit-test target discovery names. Add regression seeds for panics, boundary timestamps, invalid UTF-8/time strings, decimal edge cases, row encodings, and codec length boundaries.
