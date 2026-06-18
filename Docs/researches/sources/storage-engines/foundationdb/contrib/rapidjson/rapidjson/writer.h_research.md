# sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/writer.h

## Purpose

`writer.h` implements RapidJSON's SAX-style JSON generator. `Writer` receives handler events or direct method calls and writes syntactically correct compact JSON to an output stream while tracking object/array nesting.

## Important APIs and Types

`Writer<OutputStream, SourceEncoding, TargetEncoding, StackAllocator, writeFlags>` implements the handler methods `Null`, `Bool`, integer and double overloads, `RawNumber`, `String`, `StartObject`, `Key`, `EndObject`, `StartArray`, and `EndArray`. It also exposes `Reset`, `IsComplete`, `GetMaxDecimalPlaces`, `SetMaxDecimalPlaces`, string/key convenience overloads, and `RawValue`. `WriteFlag` controls encoding validation and NaN/Inf emission. Internal `Level` records whether a nested level is an array and how many values have been emitted.

## Control Flow

Each public value method calls `Prefix` to emit required separators and enforce object key position assertions, writes the value, then calls `EndValue` to flush when the root value is complete. Objects and arrays push a `Level` after writing `{` or `[`, and pop it before writing `}` or `]`. Scalars use internal integer/double conversion helpers. Strings reserve worst-case escaped capacity, write a quote, stream through source characters, emit required escapes or Unicode surrogate pairs, optionally validate encoding, then write the closing quote. `RawValue` injects caller-provided JSON without validation beyond assertions.

## State and Persistence

The writer keeps a pointer to the current output stream, a stack of nesting `Level` objects, `maxDecimalPlaces_`, and `hasRoot_`. `Reset` replaces the stream, clears nesting, and permits reuse for another JSON document. Persistent output is owned by the supplied stream, commonly `StringBuffer`; the writer itself stores only generation state.

## Dependencies and Integration Points

The header depends on `stream.h`, `stringbuffer.h`, `internal::Stack`, string length helpers, integer/double conversion helpers, and optional SSE2/SSE4.2 intrinsics. It is the canonical output handler for `Reader::Parse` and `Document::Accept`, and it has full specializations for `Writer<StringBuffer>` to write numbers and SIMD-scanned string chunks directly into the buffer.

## Risks and Edge Cases

Structural correctness is enforced mostly with assertions, so release builds can generate invalid JSON if calls are made out of sequence. `RawValue` trusts the caller to provide well-formed JSON. NaN and Infinity are rejected unless the write flags allow them, and those outputs are not standard JSON. `SetMaxDecimalPlaces` truncates some double renderings and can affect round-trip precision. The `Writer<StringBuffer>::WriteDouble` specialization checks `kWriteDefaultFlags` for NaN/Inf rather than the template `writeFlags`, which is worth regression testing if non-default flags are used with the specialization.

## Test Signals

Tests should cover scalar rendering, nested object/array separator placement, object key assertions, reset and complete-state behavior, string escaping and Unicode transcoding, invalid encoding with validation enabled, raw values, decimal-place truncation, NaN/Inf gating, `StringBuffer` specializations, SIMD and non-SIMD string paths, and reader-to-writer round trips.
