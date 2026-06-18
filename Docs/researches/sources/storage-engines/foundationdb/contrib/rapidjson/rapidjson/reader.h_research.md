# sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/reader.h

## Purpose

`reader.h` implements RapidJSON's SAX-style JSON parser. `GenericReader` reads JSON from a `Stream`, emits synchronous handler events, supports recursive and iterative parsing modes, and is the primary event source used by `Document`, `SchemaValidatingReader`, and callers that stream JSON without building a DOM.

## Important APIs and Types

The public parse surface is `GenericReader<SourceEncoding, TargetEncoding, StackAllocator>::Parse<parseFlags>(InputStream&, Handler&)`, plus error accessors `HasParseError`, `GetParseErrorCode`, and `GetErrorOffset`. `Reader` aliases UTF-8 source/target parsing. `ParseFlag` configures in-situ parsing, encoding validation, iterative parsing, stop-when-done behavior, full-precision numbers, comments, number-as-string mode, trailing commas, and NaN/Inf acceptance. `BaseReaderHandler` defines default no-op handler behavior, and the handler concept includes scalar events, `RawNumber`, strings/keys, and object/array boundaries.

## Control Flow

Normal `Parse` clears the previous `ParseResult`, installs an RAII stack clearer, skips whitespace/comments, rejects empty input, parses one root value, and optionally checks for root singularity. `ParseValue` dispatches by leading character to object, array, string, literal, or number parsers. Objects and arrays loop through members/elements, call handler begin/end events, count children, enforce commas/colons/brackets, and optionally accept trailing commas. Strings are decoded through `ParseStringToStream`, handling escapes, surrogate pairs, optional transcoding validation, and SIMD fast paths for unescaped byte scans. Numbers are parsed through `NumberStream`, selecting int, uint, int64, uint64, double, raw number, or NaN/Inf handler events based on flags and range.

Iterative parsing replaces recursive descent with a small predictive state machine. It tokenizes the next byte, uses a state/token transition table, pushes parent state and member/element counts on `internal::Stack`, and calls the same scalar/string/object/array handlers during transitions. `HandleError` maps parser states to specific `ParseErrorCode` values when the state machine reaches an invalid transition or EOF too early.

## State and Persistence

The reader persists no JSON data beyond the current parse. Per-instance state is an `internal::Stack` used for decoded non-in-situ strings, full-precision number buffers, and iterative parser frames, plus the last `ParseResult`. In-situ parsing writes decoded strings back into the mutable input stream. `ClearStackOnExit` clears transient stack memory after parse completion or exception-style early exits.

## Dependencies and Integration Points

The header depends on RapidJSON allocators, stream abstractions, encoded streams, transcoding/encoding primitives, `internal::Stack`, `internal::strtod`, and error definitions. It has optional SSE2/SSE4.2 acceleration for whitespace and unescaped string scanning. `SchemaValidatingReader` and DOM `Document` parsing rely on this reader's handler protocol, and `RAPIDJSON_PARSE_ERROR_NORETURN` is a customization point for projects that throw exceptions instead of storing parse results.

## Risks and Edge Cases

The parser assumes stream implementations correctly provide null-terminated or sentinel-backed input; SIMD paths read aligned 16-byte blocks after alignment checks and therefore are sensitive to invalid buffer contracts. In-situ parsing is destructive and returns non-copy string pointers into the input. Handler methods can terminate parsing by returning false, which becomes `kParseErrorTermination`. Full-precision numeric parsing is slower and uses temporary stack buffers. NaN/Inf, comments, and trailing commas are non-standard and only accepted when explicitly flagged. `kParseStopWhenDoneFlag` allows trailing data to remain unread after a valid root.

## Test Signals

Useful tests include strict JSON root singularity, empty and malformed object/array syntax, all parse flags, comment and trailing-comma acceptance/rejection, in-situ decoded string mutation, invalid escape and surrogate handling, encoding validation failures, integer boundary promotion to 64-bit or double, exponent overflow, full-precision round trips, NaN/Inf gating, handler termination, iterative-vs-recursive parity, and SIMD/non-SIMD builds.
