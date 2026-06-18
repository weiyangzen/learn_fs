# sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/prettywriter.h

Purpose: `PrettyWriter` extends `Writer` with indentation, newlines, spaces, and optional single-line arrays while preserving the SAX handler interface.

Important APIs and types: `PrettyFormatOptions` defines `kFormatDefault` and `kFormatSingleLineArray`. `PrettyWriter<OutputStream, SourceEncoding, TargetEncoding, StackAllocator, writeFlags>` inherits `Writer` and implements handler methods `Null`, `Bool`, integer/uint/double numbers, `RawNumber`, `String`, `StartObject`, `Key`, `EndObject`, `StartArray`, `EndArray`, and `RawValue`. Configuration methods are `SetIndent()` and `SetFormatOptions()`.

Control flow: Each value method calls `PrettyPrefix(type)` before delegating to base write methods. `PrettyPrefix()` inspects the top level stack: arrays get commas and either spaces or newline+indent; objects alternate between key positions and value positions, emitting commas/newlines between members and colon-space between key and value. End methods pop level state, optionally write closing indentation, and flush when the root completes.

State and persistence behavior: State is inherited writer state plus `indentChar_`, `indentCharCount_`, and `formatOptions_`. The underlying output stream receives bytes/chars; no filesystem persistence is owned by the writer.

Dependencies and integration points: It includes `writer.h`, relies on base `Level` stack and write primitives, uses `internal::StrLen` for convenience overloads, and `PutN` for indentation.

Risks: Object member sequencing is enforced by assertions only; invalid SAX event order can produce invalid output in release builds. `RawValue()` may not be re-indented internally. The second constructor does not initialize `formatOptions_` in this copy, so using it before `SetFormatOptions()` risks indeterminate formatting behavior.

Test signals: Cover object/array pretty output, empty containers, nested indentation, tabs/newline indent chars, single-line arrays, root-only flush, invalid event assertions in debug, raw value insertion, and constructor behavior without an immediate output stream.
