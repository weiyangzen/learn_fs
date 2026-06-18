# Research: sources/storage-engines/wiredtiger/test/3rdparty/nlohmann/json.hpp

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-009000`: lines 1-6198, `Docs/researches/chunks/subset-b-009000_research.md`
- `subset-b-009001`: lines 6199-13906, `Docs/researches/chunks/subset-b-009001_research.md`
- `subset-b-009002`: lines 13907-21115, `Docs/researches/chunks/subset-b-009002_research.md`
- `subset-b-009003`: lines 21116-25526, `Docs/researches/chunks/subset-b-009003_research.md`

## Chunk Research

### subset-b-009000: lines 1-6198

# sources/storage-engines/wiredtiger/test/3rdparty/nlohmann/json.hpp lines 1-6198

Purpose: this chunk is the opening portion of the vendored single-header `nlohmann/json.hpp` 3.12.0 used by WiredTiger tests. It establishes the library version/ABI namespace, portability and compiler-feature macros, public serialization helper macros, forward declarations for `basic_json`, the core JSON type enum, metadata/type-trait machinery, exception classes, conversion overloads for C++/STL types, and the start of binary subtype support. It is infrastructure for the later `basic_json` class definition rather than WiredTiger-specific logic.

Important APIs, types, and functions:

- Version and ABI macros define `NLOHMANN_JSON_VERSION_MAJOR/MINOR/PATCH` as 3.12.0 and construct the inline namespace from version plus ABI-affecting feature flags: diagnostics, diagnostic byte positions, and legacy discarded-value comparison. `NLOHMANN_JSON_NAMESPACE_BEGIN/END` and `NLOHMANN_JSON_NAMESPACE` wrap all exported library symbols.
- `detail::void_t`, `detail::nonesuch`, `detail::detector`, `is_detected`, `detected_t`, `detected_or_t`, `is_detected_exact`, and `is_detected_convertible` provide C++11-compatible SFINAE detection used throughout serializer selection and container compatibility checks.
- The Hedley block defines `JSON_HEDLEY_*` feature probes and attributes for many compilers. It normalizes version checks, pragma support, diagnostic push/pop, cast wrappers, `deprecated`, `warn_unused_result`, `noreturn`, `unreachable`, branch prediction, `malloc`/`pure`/`const`, inline/visibility/nothrow/fallthrough annotations, static assertions, C/C++ linkage helpers, warning/message pragmas, and deprecated compatibility aliases.
- Internal macro-scope configuration detects supported compilers, C++ language level (`JSON_HAS_CPP_11/14/17/20/23`), filesystem availability, ranges, three-way comparison, static RTTI, inline variables, `[[no_unique_address]]`, exception support, user-overridden exception/assert macros, implicit conversions, enum serialization, and global UDL behavior.
- Public serialization macros include `NLOHMANN_JSON_SERIALIZE_ENUM`, `NLOHMANN_DEFINE_TYPE_INTRUSIVE`, `NLOHMANN_DEFINE_TYPE_NON_INTRUSIVE`, their `_WITH_DEFAULT` and `_ONLY_SERIALIZE` variants, and derived-type variants added for 3.12.0. These expand to ADL-visible `to_json`/`from_json` functions using up to 64 listed data members.
- Forward declarations expose `template<class...> class basic_json`, `json_pointer`, `adl_serializer`, aliases `json` and `ordered_json`, and `ordered_map`.
- `detail::value_t` enumerates stored JSON types: `null`, `object`, `array`, `string`, `boolean`, signed/unsigned/float numbers, `binary`, and `discarded`. Its ordering operator implements the library's cross-type ordering with special handling for unordered/discarded cases when C++20 comparison is available.
- JSON Pointer helpers `replace_substring`, `escape`, and `unescape` implement RFC 6901 token escaping for `~` and `/`.
- `detail::position_t` carries parser token position state: total bytes/chars read, current-line character count, and line count. It converts to `size_t` for SAX compatibility.
- C++ future/backfill utilities include `uncvref_t`, `enable_if_t`, C++11 `integer_sequence`/`index_sequence` replacements, `priority_tag`, `static_const`, and `make_array`.
- Iterator and range traits include `iterator_types`, custom `iterator_traits`, `NLOHMANN_CAN_CALL_STD_FUNC_IMPL(begin/end)`, `is_range`, `iterator_t`, and `range_value_t`, avoiding brittle `std::iterator_traits` behavior on older compilers.
- Type traits determine JSON conversion viability: `is_basic_json`, `is_basic_json_context`, `is_json_ref`, `has_from_json`, `has_non_default_from_json`, `has_to_json`, `is_getable`, comparator/key traits, object/array/string constructibility and compatibility, `is_compatible_integer_type`, tuple constructibility, JSON iterator/pointer exclusion, ordered-map detection, integer range checks, C-string detection, and transparent-comparator detection.
- `detail::concat_length`, `concat_into`, and `concat` assemble exception strings efficiently through detected `append`, `+=`, iterator, or data/size APIs.
- Exception classes define the public error taxonomy: `detail::exception`, `parse_error`, `invalid_iterator`, `type_error`, `out_of_range`, and `other_error`. They carry stable integer IDs and formatted `what()` strings. With `JSON_DIAGNOSTICS`, errors include a JSON Pointer-like path by walking parent links; with `JSON_DIAGNOSTIC_POSITIONS`, errors can include byte spans.
- `identity_tag<T>` is a dispatch tag for return-by-value `from_json` overloads, especially non-default-constructible target types.
- `detail::std_fs` aliases either `std::filesystem` or `std::experimental::filesystem` when available.
- `from_json` overloads convert JSON to `nullptr_t`, optional values, booleans, strings, arithmetic types, enum underlying values, `std::forward_list`, `std::valarray`, C arrays up to 4 dimensions, `std::array`, constructible array containers, `binary_t`, constructible object/map-like containers, tuples/pairs, non-string-key `std::map`/`std::unordered_map` represented as arrays of pairs, and filesystem paths. The inline function object `nlohmann::from_json` forwards to ADL-visible overloads.
- `iteration_proxy_value` and `iteration_proxy` implement `items()` support, yielding key/value proxy objects for arrays, objects, and primitives. `std::tuple_size` and `std::tuple_element` specializations plus `get<0/1>` enable structured bindings; ranges builds mark the proxy as a borrowed range.
- `external_constructor<value_t>` specializations centralize mutation of an existing `basic_json` into boolean, string, binary, number, array, and object values. Each destroys the old `m_data.m_value`, sets `m_data.m_type`, installs the new value, updates parent pointers for structured values, and asserts invariants.
- `to_json` overloads convert optional values, booleans including `std::vector<bool>` references, strings, floating-point and integer types, enums, arrays/ranges, `binary_t`, `std::valarray`, objects/maps, non-string C arrays, pairs, `items()` proxy values, tuples, and filesystem paths into a `BasicJsonType`. The inline function object `nlohmann::to_json` forwards to ADL-visible overloads.
- `adl_serializer<ValueType>` delegates `from_json` and `to_json` to the global ADL customization points. This is the default serializer template parameter used by `basic_json`.
- The chunk ends at the beginning of `byte_container_with_subtype<BinaryType>`, declaring `container_type` and `subtype_type`. Its constructors and subtype state are outside this chunk.

Control flow:

- Compile-time control flow dominates the first half of the chunk. Preprocessor checks decide ABI namespace spelling, available standard/library features, exception behavior, and compiler attributes before any `basic_json` code is compiled.
- Conversion selection is mostly SFINAE-driven. Traits check whether a target type looks like an object, array, string, arithmetic type, tuple, path, or user-serializable type; overload resolution then chooses the narrowest matching `from_json`/`to_json` path.
- Runtime conversion functions first validate the source JSON type with predicates such as `is_null`, `is_array`, `is_object`, `is_string`, `is_binary`, or `is_boolean`. Failures throw `type_error::create(302, ...)` through `JSON_THROW`, or abort when exceptions are disabled.
- Array/container conversion usually constructs a temporary container, transforms each JSON element with `get<T>()`, then move-assigns the result. Priority tags prefer exact `array_t`, then fixed `std::array`, then containers with `reserve`, then generic insertable containers.
- Object conversion reads the underlying `object_t` pointer and transforms each key/value pair into the target mapped type through `get<mapped_type>()`.
- Exception diagnostic path construction walks from a leaf JSON node to parents, records array indexes or object keys, escapes path tokens with the JSON Pointer helpers, and prepends that path to the error message.
- `external_constructor` is the key state transition layer for `to_json`: destroy old storage, set type tag, allocate/copy/move the new storage, restore parent links for arrays/objects, and assert invariants.

State and persistence behavior:

- This header has no direct filesystem or database persistence. It is vendored test dependency code compiled into consumers.
- Persistent runtime state belongs to `basic_json` instances, primarily `m_data.m_type`, `m_data.m_value`, optional parent pointers under diagnostics, and optional byte-position metadata under diagnostic-position builds. This chunk manipulates those fields in `external_constructor` and exception diagnostics but does not define the full storage type.
- Macro state is significant. Defining `JSON_DIAGNOSTICS`, `JSON_DIAGNOSTIC_POSITIONS`, `JSON_USE_IMPLICIT_CONVERSIONS`, `JSON_DISABLE_ENUM_SERIALIZATION`, `JSON_NOEXCEPTION`, `JSON_THROW_USER`, or namespace/version macros before including the header changes ABI, overloads, exception behavior, or generated functions.
- `iteration_proxy_value` stores iterator position, array index, cached stringified array index, and an empty string for primitive key reporting. This is transient iteration state only.
- Conversion functions mutate caller-provided target containers and scalars. Some clear or replace targets (`forward_list`, `valarray`, maps), while tuple/array identity-tag overloads return new values.

Dependencies:

- Standard library dependencies in this chunk include algorithms, arrays, containers, iterators, memory, strings, tuples, type traits, limits, exceptions, optional when C++17 is enabled, filesystem when available, ranges when available, and comparison when C++20 three-way comparison is available.
- The header depends heavily on compiler predefined macros and feature-test macros. Hedley support spans GCC, Clang, MSVC, Intel, ARM, IBM XL, TI, Cray, IAR, TinyCC, SunPro, Emscripten, and other compiler families.
- Internal dependencies include later `basic_json` APIs and fields: `is_*` predicates, `type_name`, `get_ptr`, `get<T>()`, `at`, `begin/end/rbegin/rend`, `size`, `m_data`, `set_parent(s)`, `assert_invariant`, `create`, parent links, and byte-position accessors. Those definitions are outside or later than this chunk.
- Public integration relies on ADL. User code supplies `to_json`/`from_json` functions in associated namespaces, or uses the `NLOHMANN_DEFINE_*` macros to generate them.
- WiredTiger integration is indirect: test code can include this vendored header without an external package dependency, and any compile flags/macros from WiredTiger's test build affect the generated JSON ABI and behavior.

Integration points:

- The chunk is part of an amalgamated header; comments show original component boundaries such as `adl_serializer.hpp`, `detail/abi_macros.hpp`, `detail/conversions/from_json.hpp`, `detail/exceptions.hpp`, `detail/meta/type_traits.hpp`, and `detail/conversions/to_json.hpp`.
- `NLOHMANN_BASIC_JSON_TPL_DECLARATION` and `NLOHMANN_BASIC_JSON_TPL` are used later to specialize and refer to the configurable `basic_json` template without repeating its long template parameter list.
- `adl_serializer` and the inline `to_json`/`from_json` function objects are the main public customization surface consumed by `basic_json` constructors, assignment, and `get<T>()`.
- `value_t` is the shared type tag used by storage, comparison, iterators, exceptions, parsing, and conversion. Later code depends on the exact enum values and ordering behavior.
- Exception classes are the stable public exception API exposed as nested aliases by `basic_json` later in the file.
- `iteration_proxy` integrates with `basic_json::items()` and C++ structured bindings.
- Filesystem overloads make JSON string conversion interoperate with `std::filesystem::path` when the compiler/runtime combination is accepted by the feature checks.

Risks and edge cases:

- This is third-party vendored code; local edits risk diverging from upstream nlohmann/json behavior and ABI. Version-mixing is partially detected by preprocessor warnings only.
- ABI namespace changes with diagnostics and version macros. Mixing translation units built with different macro settings can produce distinct types or linker surprises.
- `JSON_NOEXCEPTION` turns throws into `std::abort()`, so type errors and parse errors become process termination in exception-disabled builds.
- Numeric conversions use `static_cast` after type validation. Some paths intentionally allow narrowing or signedness-sensitive behavior; `is_compatible_integer_type` limits certain constructor overloads but `from_json` arithmetic extraction can still cast.
- Object and array compatibility traits are intricate and can select surprising overloads for custom containers, especially types that are both range-like and string-like or map-like.
- `std::map`/`std::unordered_map` with non-string keys deserialize from arrays of key/value arrays, not JSON objects; callers expecting object syntax need string-constructible keys.
- `from_json` for fixed C arrays indexes with `at()` but does not first check exact array size in this chunk; short JSON arrays throw through `at`, while extra JSON elements are ignored.
- Exception diagnostics require parent pointers to be maintained accurately. `external_constructor` calls `set_parent(s)` for structured values, but any later code that mutates without maintaining parents can degrade diagnostic paths.
- The Hedley and feature-detection matrix is broad. Unsupported or unusual compiler/library combinations may take fallback paths that compile but lose attributes, diagnostics, filesystem support, or performance hints.
- The assigned range ends mid-`byte_container_with_subtype`, so binary subtype construction/comparison/state behavior is only partially visible here.

Test signals:

- Compile-time coverage is the primary signal: including this header under WiredTiger's supported C++ standard and compiler matrix should pass unsupported-compiler checks, feature detection, and overload resolution.
- Serialization macro tests should cover generated intrusive/non-intrusive, defaulted, serialize-only, enum, and derived-type conversions.
- Conversion tests should exercise primitive type mismatches and confirm `type_error` id 302, numeric casts, enum serialization toggling, optional null/non-null behavior, STL container round trips, tuple/pair round trips, non-string-key map array-pair encoding, filesystem path conversion when enabled, and `items()` structured bindings.
- Diagnostic builds should verify JSON Pointer path escaping (`~` to `~0`, `/` to `~1`) and optional byte-position text in exceptions.
- Exception-disabled builds should be tested separately because error paths abort instead of throwing.
- For WiredTiger specifically, the useful guard is that tests including the vendored header compile without requiring a system nlohmann/json install and without macro conflicts from the broader test build.

### subset-b-009001: lines 6199-13906

# sources/storage-engines/wiredtiger/test/3rdparty/nlohmann/json.hpp lines 6199-13906

## Scope

This chunk covers a large middle section of the vendored nlohmann JSON single-header library used by WiredTiger tests. It starts at the end of `byte_container_with_subtype`, continues through JSON hashing, input adapters, the text JSON lexer, SAX handlers, SAX concept checks, binary-format readers for BSON/CBOR/MessagePack/UBJSON/BJData, the recursive-descent JSON parser, and the beginning of iterator support. The range ends inside `detail::iter_impl::operator->`, so iterator behavior after the binary value case is outside this chunk.

The file is a third-party dependency (`JSON for Modern C++`, version 3.12.0) under `test/3rdparty`. It should be treated as vendored library code rather than WiredTiger-owned storage-engine logic.

## Purpose

The code in this range provides the deserialization and traversal core for `nlohmann::basic_json`:

- binary values can carry optional subtypes through `byte_container_with_subtype`;
- `detail::hash` computes type-aware recursive hashes for JSON values;
- input adapters normalize `FILE*`, streams, containers, iterators, C strings, spans, and wide strings into a byte-oriented reader interface;
- `detail::lexer` tokenizes RFC 8259 JSON text, including UTF-8 validation, escape decoding, number parsing, comment skipping when enabled, BOM handling, and diagnostics;
- `json_sax` defines the event interface consumed by text and binary parsers;
- DOM SAX implementations build `basic_json` values, optionally applying user callbacks that can discard parsed subtrees;
- `binary_reader` maps BSON, CBOR, MessagePack, UBJSON, and BJData bytes into the same SAX event stream;
- `parser` implements non-recursive recursive-descent JSON syntax analysis over lexer tokens;
- `primitive_iterator_t`, `internal_iterator`, and the beginning of `iter_impl` provide uniform iteration over objects, arrays, and primitive JSON values.

Within WiredTiger, this header supports tests that need JSON parsing/serialization without linking an external JSON package. The chunk does not directly interact with WiredTiger persistence, cache, log, or storage-engine state.

## Important APIs, Types, and Functions

- `byte_container_with_subtype<BinaryType>` tail: constructors from byte containers with and without subtype, equality/inequality, `set_subtype`, `subtype`, `has_subtype`, and `clear_subtype`. The subtype state is separate from the inherited byte container and uses `-1` as the public sentinel when absent.
- `detail::combine` and `detail::hash(const BasicJsonType&)`: type-aware hash helpers. They include the JSON value type, object keys and values, array elements, primitive payloads, and binary subtype metadata.
- `enum class input_format_t`: identifies `json`, `cbor`, `msgpack`, `ubjson`, `bson`, and `bjdata`.
- Input adapters: `file_input_adapter`, `input_stream_adapter`, `iterator_input_adapter`, `wide_string_input_adapter`, `iterator_input_adapter_factory`, container and pointer overloads of `input_adapter`, and `span_input_adapter`.
- `lexer_base::token_type`: the token vocabulary used by the text parser, including literals, structural tokens, numeric token classes, `parse_error`, `end_of_input`, and diagnostic-only `literal_or_value`.
- `lexer<BasicJsonType, InputAdapterType>`: scans strings, comments, numbers, literals, whitespace, BOM, and single tokens. Public getters expose parsed numbers, string buffers, token text, error messages, and `position_t`.
- `json_sax<BasicJsonType>`: abstract event interface for null, boolean, signed/unsigned/float numbers, strings, binary values, object/array starts and ends, object keys, and parse errors.
- `json_sax_dom_parser`: SAX sink that constructs a full DOM in a referenced `BasicJsonType`, using `ref_stack` and `object_element` to track nesting and pending object keys.
- `json_sax_dom_callback_parser`: SAX sink that constructs a DOM while invoking `parser_callback_t` at object, array, key, and value events. It uses `keep_stack` and `key_keep_stack` to discard rejected subtrees or object members.
- `json_sax_acceptor`: SAX sink used by `accept`; it returns true for all valid events and false on parse error without storing a DOM.
- `is_sax` and `is_sax_static_asserts`: compile-time checks that a SAX type has the complete callback surface with exact `bool` return types.
- `enum class cbor_tag_handler_t`: controls CBOR tag behavior as `error`, `ignore`, or `store`.
- `binary_reader<BasicJsonType, InputAdapterType, SAX>`: deserializes BSON, CBOR, MessagePack, UBJSON, and BJData to SAX callbacks.
- `parse_event_t` and `parser_callback_t`: callback event taxonomy and function signature for text JSON parsing with filtering.
- `parser<BasicJsonType, InputAdapterType>`: public `parse`, `accept`, and `sax_parse` APIs over the lexer.
- `primitive_iterator_t`, `internal_iterator<BasicJsonType>`, and partial `iter_impl<BasicJsonType>`: storage and dereference logic for basic JSON iterators.

## Control Flow

Text JSON parsing flows through `input_adapter(...)` into `lexer`, then through `parser::sax_parse_internal`. The parser reads one token ahead with `get_token`, dispatches primitive tokens directly to SAX callbacks, and tracks nested arrays/objects with a `std::vector<bool>` where `true` means array and `false` means object. Objects require a string key, a name separator, then a value. Arrays accept values separated by commas. Once a value completes, the parser evaluates the current container state to decide whether to consume a comma, close a container, or report a syntax error.

`lexer::scan` first handles a UTF-8 BOM at the beginning of input, skips whitespace, optionally skips `//` and `/* */` comments, and then dispatches by the current byte. Strings are scanned until a closing quote while rejecting unescaped control characters, decoding JSON escapes, validating UTF-8 byte sequences, and composing Unicode surrogate pairs from `\uXXXX` escapes. Numbers are scanned by a label-based deterministic finite state machine derived from RFC 8259, then converted with `strtoull`, `strtoll`, or floating-point conversion. Locale-dependent decimal separators are normalized internally and restored to `.` when exposing the token string.

DOM construction is SAX driven. `json_sax_dom_parser::handle_value` stores the first value as the root, appends array elements to the current array, or assigns object values through the previously captured `object_element`. Object and array starts push the new container pointer on `ref_stack`, and end events pop it. Callback parsing follows the same structure but calls the user callback to decide whether to keep values, keys, objects, or arrays.

Binary parsing starts at `binary_reader::sax_parse`, which selects the format-specific parser and then, in strict mode, verifies there is no trailing data. BSON reads document and array element lists, dispatches BSON element type bytes, and supports doubles, strings, nested objects/arrays, binary, booleans, null, int32, int64, and uint64 while rejecting unsupported record types. CBOR dispatches major-type byte ranges for integers, byte strings, UTF-8 strings, arrays, maps, tags, booleans, null, and floats; indefinite-length strings, binaries, arrays, and maps loop until the break byte. MessagePack dispatches fixint/fixmap/fixarray/fixstr plus typed number, string, binary, extension, array, and map markers. UBJSON and BJData parse marker-prefixed scalar values, optimized containers with optional type and size metadata, no-op `N` bytes, high-precision numeric strings, BJData unsigned widths, half floats, binary optimized arrays, and BJData ND-array conversion into JData-style annotated objects.

Iterator flow in this chunk initializes `iter_impl` storage based on the owning JSON type. `set_begin` and `set_end` bind object and array iterators to their container boundaries; null begin is set equal to end; primitive values expose a single synthetic element. `operator*` returns object member values, array elements, or the owning primitive value when the primitive iterator is at begin, and throws `invalid_iterator` for null or past-end primitive positions. The range ends while `operator->` is handling the same object/array/primitive split.

## State and Persistence Behavior

All state in this chunk is in-memory parser, iterator, and value-construction state. There are no file writes, WiredTiger metadata updates, database checkpoints, transaction commits, or durable side effects.

Important transient state includes:

- input adapter cursor state, such as `FILE*`, `std::istream`/`streambuf`, or iterator pairs;
- wide-string adapter buffers that translate UTF-16/UTF-32 code units to UTF-8 bytes;
- lexer position counters, `current`, `next_unget`, `token_string`, `token_buffer`, parsed numeric fields, and locale decimal metadata;
- SAX DOM stacks (`ref_stack`, `keep_stack`, `key_keep_stack`) and pending `object_element` pointers;
- binary-reader `current`, `chars_read`, selected `input_format`, endianness flag, SAX pointer, and BJData lookup tables;
- parser `last_token`, callback, lexer, and exception policy;
- iterator owner pointer plus `internal_iterator` union-like storage for object, array, or primitive positions.

The input stream adapter deliberately clears most stream flags on destruction while preserving EOF state, because it reads through the stream buffer rather than normal formatted stream APIs. Binary containers persist subtype information inside `basic_json` binary values after parsing CBOR tags with `store`, MessagePack extension types, or BSON binary subtype bytes.

## Dependencies and Integration Points

- Standard library dependencies include iterators, streams, `FILE*`, strings, vectors, arrays, type traits, memory, numeric conversion, locale, `snprintf`, `memcpy`, `ldexp`, `isfinite`, hashing, and optional C++23 `std::byteswap`.
- Library-internal dependencies include `value_t`, `parse_error`, `out_of_range`, `invalid_iterator`, `exception`, `position_t`, `char_traits`, `iterator_traits`, detection/type-trait helpers, `concat`, `conditional_static_cast`, `value_in_range_of`, `make_array`, ABI/macro wrappers, and `JSON_ASSERT`/`JSON_THROW`.
- `basic_json` integration is heavy: the code uses `BasicJsonType` aliases for numbers, strings, binary containers, object/array storage, parser callbacks, exception types, allocator behavior through containers, max-size checks, parent-link maintenance, and optional diagnostic positions.
- Text and binary parsers share the SAX contract. Any custom SAX consumer used with `sax_parse` must satisfy the exact `is_sax_static_asserts` surface, including binary values and parse-error handling.
- Binary formats integrate with public APIs such as `from_cbor`, `from_msgpack`, `from_ubjson`, `from_bjdata`, and `from_bson` elsewhere in the header. This chunk supplies the core reader they call.
- Iterators integrate with `basic_json::begin`, `end`, `items`, object key/value iteration, array traversal, and primitive single-value iteration.
- WiredTiger integration is indirect: test code can include this vendored header and rely on consistent JSON behavior without involving WiredTiger build artifacts beyond include paths and compiler settings.

## Risks and Maintenance Notes

- This is vendored third-party code. Local edits risk diverging from upstream nlohmann behavior and should generally be avoided unless the vendored dependency is intentionally patched.
- Large untrusted inputs can consume memory while building strings, binaries, arrays, objects, or DOM trees. The code avoids pre-reserving huge string/binary sizes in some paths, but it still appends/read-loops until declared lengths, EOF, or allocation failure.
- Parser recursion is mostly avoided in text JSON by using an explicit state stack, but binary CBOR, MessagePack, BSON, and UBJSON parsing uses recursive calls for nested values and containers. Deep binary nesting can therefore stress call depth.
- Several binary length conversions rely on `conditional_static_cast`, `value_in_range_of`, and explicit overflow checks. Maintenance around new integer widths or BJData extensions must preserve those guards.
- CBOR tag handling is security-relevant. With `error`, tags are rejected; with `ignore`, tag metadata is skipped; with `store`, supported tag lengths become binary subtypes and the next item is expected to be binary. Callers must choose behavior deliberately.
- BSON support is intentionally partial. Unsupported element type bytes report parse error 114. Tests relying on broader BSON types would fail until additional cases are implemented.
- UTF handling is strict for JSON text strings, but wide-string adapters perform UTF-16/UTF-32 to UTF-8 conversion with limited validation of malformed surrogate usage before the lexer sees bytes. Wide string binary parsing is explicitly rejected.
- Locale handling in numeric scanning is subtle: conversion uses the active C locale decimal point internally while public token strings are normalized back to `.`. Locale-dependent regressions are easy around float parsing.
- `input_adapter(CharT b)` for null-terminated byte pointers uses `strlen`, so embedded NUL bytes truncate text input unless callers pass an explicit range/span.
- `span_input_adapter::get()` returns an rvalue reference to its stored adapter. Misuse after move would be invalid, but the class exists specifically to support `{ptr, len}` adapter construction patterns.
- `json_sax_dom_parser::key` uses `operator[]`, so duplicate object keys overwrite prior values according to `basic_json` object semantics.
- Callback parsing can discard data and then sets a discarded top-level result to null. Tests for callback behavior need to distinguish parse failure from intentional discard.
- Iterator safety relies on assertions for initialized iterators and throws for invalid dereference paths. Behavior with disabled assertions and uninitialized iterators remains undefined per the local comments.

## Test Signals

Useful validation for this chunk includes:

- JSON text parser tests for literals, empty input, trailing input under strict mode, arrays/objects, duplicate keys, callback discard behavior, and `accept` versus `parse`.
- String tests for escapes, Unicode surrogate pairs, malformed `\u` sequences, unescaped control characters, valid and invalid UTF-8, BOM handling, and optional comment skipping.
- Numeric tests for signed, unsigned, floating, exponent, overflow-to-float fallback, non-finite float rejection in text parsing, and locale decimal-point behavior.
- Input adapter tests for `FILE*`, `istream`, lvalue/rvalue streams, iterator ranges, containers, C strings, arrays, spans, null pointer rejection, wide UTF-16/UTF-32 strings, and binary rejection on wide input.
- SAX tests using custom SAX classes to verify compile-time interface checks and event ordering for primitives, objects, arrays, keys, binary values, and parse errors.
- Binary-format round trips and malformed-input tests for BSON, CBOR, MessagePack, UBJSON, and BJData, including strict EOF behavior, unexpected EOF diagnostics, unsupported BSON types, CBOR indefinite containers, CBOR tag modes, MessagePack extension subtype storage, UBJSON optimized containers, BJData unsigned markers, binary optimized arrays, ND-array conversion, and high-precision numbers.
- Endianness-sensitive tests for numeric decoding on little- and big-endian hosts or through targeted byte-swap unit tests.
- Hash tests showing different values for different JSON types with similar payloads, object key/value contribution, array ordering, binary byte contents, and binary subtype presence.
- Iterator tests for begin/end on null, primitives, arrays, and objects; dereference and arrow behavior; const/non-const conversion; and invalid dereference exceptions.

### subset-b-009002: lines 13907-21115

# sources/storage-engines/wiredtiger/test/3rdparty/nlohmann/json.hpp lines 13907-21115

## Scope

This chunk covers a large middle section of the vendored nlohmann JSON single-header library, version 3.12.0. It starts near the end of `detail::iter_impl`, then includes reverse iterators, the default/custom base-class adapter, the full `json_pointer` implementation, `json_ref`, output adapters, binary serializers for BSON/CBOR/MessagePack/UBJSON/BJData, decimal floating-point formatting, textual JSON serialization, `ordered_map`, and the beginning of `basic_json` through its early constructors and storage machinery.

This is library infrastructure rather than WiredTiger-specific logic. WiredTiger tests include it as a third-party dependency, so the important integration surface is the public nlohmann JSON API and the binary/text encoders used by tests or utilities that instantiate `nlohmann::json` from this header.

## Purpose

- Provide STL-style iterator behavior for JSON values, including random-access behavior for arrays and primitive pseudo-iteration, while rejecting invalid operations on object iterators.
- Implement JSON Pointer per RFC 6901, including token parsing, escaping, checked/unchecked lookup, creation during unflattening, containment tests, flatten/unflatten support, pointer composition, and comparison operators.
- Provide lightweight helper types used by `basic_json`: a default empty base class for optional custom base support, `json_ref` for initializer-list construction without unnecessary copies, and `ordered_map` for insertion-order-preserving object storage.
- Provide output adapter abstraction so serializers can write to strings, byte vectors, and output streams through a uniform `write_character` / `write_characters` protocol.
- Serialize JSON values to binary formats: BSON, CBOR, MessagePack, UBJSON, and BJData, including binary subtype handling and optimized homogeneous container encodings.
- Serialize JSON values to textual JSON with pretty-print support, ASCII escaping, UTF-8 validation/recovery policies, locale-independent float output, and binary values represented as JSON objects with `bytes` and `subtype`.
- Start defining `basic_json` itself: public aliases, exception aliases, object/array/string/number/binary type aliases, allocator-backed `json_value` storage, invariant checks, diagnostics parent tracking, metadata reporting, and initial construction APIs.

## Important APIs, Types, And Functions

- `detail::iter_impl` operators in this chunk implement increment/decrement, comparisons, offset arithmetic, indexing, `key()`, and `value()`. They switch on the owning `basic_json` value type and throw `invalid_iterator` for object offset/order operations or invalid primitive dereferences.
- `detail::json_reverse_iterator<Base>` wraps `std::reverse_iterator<Base>` and preserves JSON-specific `key()` and `value()` access by looking at `--base()`.
- `detail::json_default_base` and `detail::json_base_class<T>` ensure `basic_json` always has a base class, using an empty type when the `CustomBaseClass` template parameter is `void`.
- `nlohmann::json_pointer<RefStringType>` stores `reference_tokens` and exposes `to_string()`, conversion to string, stream output, `/=` and `/` composition, `parent_pointer()`, `pop_back()`, `back()`, `push_back()`, `empty()`, and comparison operators.
- `json_pointer::array_index<BasicJsonType>()` validates array token syntax, forbids leading zeroes, converts with `std::strtoull`, detects `ERANGE`, and checks the result against `BasicJsonType::size_type`.
- `json_pointer::get_unchecked()`, `get_checked()`, `contains()`, `get_and_create()`, `flatten()`, and `unflatten()` are private friend-facing algorithms used by `basic_json` pointer APIs and by flatten/unflatten features.
- `detail::json_ref<BasicJsonType>` is a move-only wrapper that either stores an owned JSON value or references an existing value. `moved_or_copied()` returns by move for owned values and by copy for references.
- `detail::output_adapter_protocol`, `output_vector_adapter`, `output_stream_adapter`, `output_string_adapter`, and `output_adapter` abstract serialization sinks behind `std::shared_ptr`.
- `detail::binary_writer<BasicJsonType, CharType>` exposes `write_bson()`, `write_cbor()`, `write_msgpack()`, and `write_ubjson()`. Private helpers calculate BSON sizes, write endian-correct numbers, choose compact float encodings, choose UBJSON/BJData numeric prefixes, and emit BJData ndarray objects when the `_ArrayType_`, `_ArraySize_`, and `_ArrayData_` shape is recognized.
- `detail::dtoa_impl` implements Grisu2-style float-to-decimal conversion using `diyfp`, cached powers, boundary computation, digit generation, rounding, exponent formatting, and fixed/exponential layout.
- `detail::to_chars()` wraps the DTOA implementation for finite IEEE float/double values and formats zero as `0.0`.
- `detail::serializer<BasicJsonType>` exposes `dump()` for textual JSON and contains `dump_escaped()`, `dump_integer()`, `dump_float()`, UTF-8 `decode()`, and locale cleanup for fallback `snprintf` float formatting.
- `nlohmann::ordered_map<Key, T, ...>` is a `std::vector<std::pair<const Key, T>>`-backed associative container with linear `emplace`, `operator[]`, `at`, `erase`, `count`, `find`, and `insert`, preserving insertion order and supporting transparent key lookup where available.
- The `basic_json` opening section declares friend internals, public type aliases, `meta()`, `create<T>()`, the `json_value` union and its `destroy()` method, diagnostic parent setters, parser callback aliases, and constructors for null, explicit type, compatible types, other `basic_json` instantiations, initializer lists, binary values, arrays, objects, repeated arrays, and iterator ranges.

## Control Flow

Iterator operations route through the owning value's `m_data.m_type`. Object iterators delegate to the object container iterator for movement and equality, but order comparisons and offsets throw because object iterators are not random-access in this API. Array iterators use the array container iterator. Primitive values use a `primitive_iterator_t` that represents begin/end over a single scalar value. Equality also accepts value-initialized iterators and treats two null-owned iterators as equal.

JSON Pointer construction calls `split()`, which enforces an empty string or leading slash, splits on slash boundaries, validates every `~` escape, unescapes tokens, and stores them. Lookup then walks tokens against the current JSON type. Checked lookup uses `at()` and throws on missing keys or out-of-range indexes. Unchecked mutable lookup creates arrays or objects when the current value is null, treats `-` as append position for arrays, and uses `operator[]`. Const unchecked lookup cannot use `-` and throws if resolution fails. `contains()` follows the same traversal without mutating and returns false for syntactically invalid array tokens, missing keys, out-of-range indexes, or primitive intermediates.

Flattening recursively descends arrays and objects, building escaped pointer strings as keys in an output object. Empty arrays and objects become `null` at their reference string. Unflattening requires an object whose values are primitive, then constructs a fresh result by assigning each primitive through `json_pointer(element.first).get_and_create(result)`.

Binary output flows through an output adapter. `write_cbor()` and `write_msgpack()` switch directly on JSON type and emit format markers, lengths, and payload bytes recursively for arrays/objects. `write_ubjson()` handles optional count and type prefixes; for homogeneous containers it can elide per-element type markers. In BJData mode it uses additional unsigned integer markers and can encode JData-style ndarray objects as typed arrays. `write_bson()` requires a top-level object, calculates embedded document sizes before emission, then writes length-prefixed little-endian BSON objects/arrays with typed entries.

Textual serialization is recursive. `serializer::dump()` writes objects and arrays with either compact separators or indentation/newline formatting, serializes strings through `dump_escaped()`, serializes binary values as `{"bytes":[...],"subtype":...}`, emits non-finite floats as `null`, and emits discarded values as the literal `<discarded>`. `dump_escaped()` runs a DFA UTF-8 decoder, writes JSON escapes for control characters, quotes, backslashes, and optionally non-ASCII code points, and applies the configured error policy: strict throws, ignore drops invalid sequences, replace writes U+FFFD.

The beginning of `basic_json` centralizes all allocation of heap-backed value types through `create<T>()`, which uses the configured allocator and a temporary `unique_ptr` deleter for exception safety. `json_value(value_t)` constructs the active union member for empty objects, arrays, strings, binary values, booleans, numbers, or null. `destroy(value_t)` first flattens nested arrays/objects into a heap-allocated vector stack so deeply nested values do not recursively destroy on the C++ call stack, then destroys and deallocates the active heap member.

Constructors in this chunk either set `m_data` directly, delegate to serializer hooks, or inspect inputs to decide the JSON type. Initializer-list construction checks whether every element is a two-element array with a string key and, if so, creates an object; otherwise it creates an array unless the caller explicitly requested object construction, in which case incompatible input throws `type_error.301`.

## State And Persistence Behavior

The code has no external persistence of its own. It mutates in-memory JSON values and writes serialized bytes or characters to caller-provided sinks. Persistence is indirect: callers may store the emitted BSON, CBOR, MessagePack, UBJSON/BJData, or textual JSON elsewhere.

Important in-memory state includes:

- `json_pointer::reference_tokens`, a vector of unescaped path tokens.
- `output_adapter` shared pointers that reference caller-owned vectors, strings, or streams; the adapters do not own the underlying sink object.
- `binary_writer::oa` and `serializer::o`, which hold output adapters and must remain non-null.
- `serializer` buffers: `number_buffer` for integers/floats, `string_buffer` for escaped strings, and `indent_string` that grows as pretty-print depth increases.
- `serializer` locale snapshot fields `thousands_sep` and `decimal_point`, used only for fallback floating output cleanup.
- `ordered_map` state in its vector base; object insertion order is the vector order.
- `basic_json::m_data`, whose `m_type` selects the active member of the `json_value` union. Object, array, string, and binary values are heap allocated through the configured allocator; primitive values live directly in the union.
- Optional diagnostic parent pointers under `JSON_DIAGNOSTICS`, updated by `set_parents()`, `set_parent()`, and range parent helpers when structured values are created or inserted.

The `basic_json::meta()` function creates a JSON object reporting library name/version, platform, compiler, and C++ language version at compile time. It is runtime data but not persistent unless a caller serializes it.

## Dependencies And Integration Points

- This chunk is part of the amalgamated nlohmann header and depends heavily on earlier definitions in the same file: `value_t`, exceptions, macros, type traits, string escaping/concatenation helpers, `binary_reader`, parser types, `json_sax`, and the `NLOHMANN_BASIC_JSON_TPL` template macros.
- Standard library dependencies include algorithms, arrays, maps, vectors, strings, iterators, memory/allocators, streams, locales, numeric limits, C string functions, `errno`, `strtoull`, math functions, and type traits.
- The iterator, pointer, serializer, binary writer, parser, and SAX classes are all friends of `basic_json`, so they integrate by directly reading or mutating `m_data` internals instead of using only public APIs.
- `json_pointer` is a public alias inside `basic_json` and supports both direct user-facing pointer operations and internal flatten/unflatten implementation.
- `output_adapter` is the bridge used by public dump and binary serialization APIs to write to strings, byte containers, and streams.
- `ordered_map` is available as an alternative `ObjectType` template argument for `ordered_json`, trading lookup cost for insertion-order retention.
- Binary writer behavior is paired with binary reader behavior defined elsewhere in the header; tests must verify format round trips across both halves.
- In this repository, integration is through vendored third-party use in WiredTiger tests. Any local code including this header receives nlohmann 3.12.0 behavior, exception IDs, formatting choices, and binary format compatibility from this implementation.

## Risks And Edge Cases

- Iterator comparisons throw when containers differ. Code that compares iterators from different JSON values is not merely false; it is an exception path.
- Object iterators reject order comparisons, offsets, and `operator[]`, while array and primitive iterators support them. Generic iterator code can accidentally trip `invalid_iterator` exceptions when run over objects.
- Primitive iterator offset semantics are unusual because a scalar acts like a one-element range; invalid primitive offsets throw `invalid_iterator.214`.
- `json_pointer::array_index()` rejects leading zeroes and non-numeric tokens and throws out-of-range errors for overflow or incomplete parsing. This strictness can surprise callers expecting permissive array index parsing.
- Mutable unchecked JSON Pointer lookup can transform null values into arrays or objects, and `"-"` appends to arrays. This is intentional but can cause hidden mutation during pointer access.
- `contains()` performs its own array-token validation before calling `array_index()`, returning false for many invalid tokens rather than throwing, while overflow inside `array_index()` may still throw.
- Flattening represents empty arrays and objects as `null`, so flatten/unflatten cannot preserve the distinction between an empty structured value and a null leaf without the documented convention.
- BSON serialization rejects top-level non-objects and keys containing embedded NUL bytes. Size fields are cast to `std::int32_t`; extremely large documents or strings are only guarded by practical memory limits and assertions in this chunk.
- CBOR and MessagePack length branches assume sizes fit supported width cases; impossible or platform-limited larger cases are often marked as coverage-excluded rather than actively handled.
- MessagePack extension subtype is written as `int8_t`, so large binary subtype values are truncated to one signed byte for ext encodings.
- UBJSON/BJData optimized container encoding relies on homogeneous prefixes. BJData ndarray encoding trusts the `_ArraySize_` values as unsigned numbers and typed array data elements as the expected numeric kinds.
- `binary_writer::write_number()` depends on `little_endianness()` from elsewhere and type punning via `memcpy`; endian handling is central to cross-platform binary compatibility.
- Textual `dump_escaped()` strict mode throws on invalid UTF-8, while replace/ignore continue. Consumers must select an error policy consistent with whether strings may contain arbitrary bytes.
- `dump_float()` emits JSON `null` for NaN and infinity, which is standards-compliant JSON but lossy for applications that expect non-finite values to round-trip.
- The fallback float path uses C locale data and then removes thousands separators and rewrites decimal points. Locale edge cases are explicitly handled but remain a portability-sensitive area.
- `ordered_map` uses linear lookup for all key operations. It preserves insertion order but can be expensive for large objects.
- `ordered_map::erase()` manually destroys and reconstructs `pair<const Key, T>` elements in place because keys are const. This is subtle allocator/lifetime code and can be sensitive to nontrivial key/value types.
- `basic_json::json_value` manually manages a tagged union. Correctness depends on `m_type` always matching the active union member and on all type-changing code calling invariant/parent maintenance.
- Deep destruction is intentionally iterative for arrays/objects; changes that reintroduce recursive destruction could make deeply nested JSON values stack-sensitive.
- Diagnostics parent pointers are conditional. Code paths must remain correct both with and without `JSON_DIAGNOSTICS`, and ordered-map vector reallocation can invalidate child addresses, requiring full parent resets.

## Test Signals

- Iterator tests should cover array, object, primitive, null, binary, discarded, const, non-const, reverse, default-constructed, and cross-container comparison paths, including expected exception IDs for invalid operations.
- JSON Pointer tests should cover escaping/unescaping, invalid `~` sequences, missing leading slash, parent/back/pop on root, pointer composition, numeric tokens with leading zeroes, `"-"` behavior, overflow indexes, checked versus unchecked lookup, const lookup, containment, flatten, and unflatten.
- Serialization round-trip tests should cover BSON, CBOR, MessagePack, UBJSON, and BJData for every JSON type, nested arrays/objects, binary values with and without subtypes, large lengths around boundary markers, signed/unsigned integer limits, floats, NaN/infinity behavior, and endian-sensitive numeric outputs.
- BJData-specific tests should include draft2 versus draft3 binary markers, optimized type/count containers, homogeneous and heterogeneous arrays/objects, and valid/invalid JData ndarray objects.
- Text dump tests should cover compact and pretty output, indentation growth, `ensure_ascii`, all JSON string escapes, valid multi-byte UTF-8, invalid UTF-8 under strict/ignore/replace, binary textual representation, locale-sensitive fallback float formatting, negative zero, integer-like floats requiring `.0`, and non-finite floats becoming `null`.
- DTOA tests should verify shortest-round-tripping output for representative float/double values, exponent formatting boundaries, fixed versus scientific notation thresholds, subnormal values, and signed zero.
- `ordered_map` tests should cover insertion-order preservation, duplicate-key insertion behavior, transparent lookup, `operator[]`, `at()` exception behavior, erase by key and iterator range, and iterator validity expectations after vector-backed modifications.
- `basic_json` construction tests should cover explicit type construction, null construction, compatible-type serialization, cross-`basic_json` conversion, initializer-list object versus array deduction, forced object errors, binary factory overloads with subtypes, repeated-value arrays, iterator-range construction, allocator behavior, and diagnostics parent invariants when enabled.

### subset-b-009003: lines 21116-25526

# sources/storage-engines/wiredtiger/test/3rdparty/nlohmann/json.hpp lines 21116-25526

## Scope

This chunk covers the tail of the vendored `nlohmann::json` single-header implementation used under WiredTiger tests. The range starts inside the iterator-range constructor for `basic_json`, then covers most public `basic_json` value lifecycle, inspection, conversion, element access, lookup, iterator, capacity, modifier, comparison, text/binary serialization, parse, JSON Pointer, JSON Patch, and Merge Patch APIs. It ends with user-defined literals, `std` specializations, optional global UDL exports, and macro cleanup for the amalgamated header.

The file is third-party code, not WiredTiger-native logic. Changes should normally come from updating the vendored nlohmann/json release rather than editing this range by hand.

## Purpose

The code in this chunk is the operational surface of `basic_json`: it defines how JSON values are copied, moved, serialized, parsed, inspected, converted to C++ types, accessed like arrays/objects, mutated, compared, patched, and translated to or from binary encodings. WiredTiger test code can include this header to build test JSON data, consume JSON test fixtures, compare generated JSON, or serialize diagnostics without depending on a system-installed nlohmann/json package.

The chunk also closes the header cleanly for consumers. It provides literals such as `"_json"`, nonmember support such as `std::hash<nlohmann::json>`, and then undefines the many feature-detection and portability macros introduced earlier in the amalgamated file.

## Important APIs, Types, and Data

- `basic_json(const basic_json&)`, `basic_json(basic_json&&)`, `operator=(basic_json)`, and `~basic_json()`: manage deep copy, move invalidation, copy/swap assignment, invariant checks, diagnostic position transfer, and destruction through the `data`/`json_value` storage layer.
- `dump(indent, indent_char, ensure_ascii, error_handler)`: serializes a value to `string_t` through `serializer` and `detail::output_adapter`.
- Type inspection helpers: `type()`, `is_null()`, `is_boolean()`, `is_number()`, `is_number_integer()`, `is_number_unsigned()`, `is_number_float()`, `is_object()`, `is_array()`, `is_string()`, `is_binary()`, `is_discarded()`, `is_primitive()`, `is_structured()`, and implicit `operator value_t()`.
- Value access: `get_ptr<T*>()`, `get<T>()`, `get_to(T&)`, `get_ref<T&>()`, implicit conversion `operator ValueType()`, and `get_binary()`. These route through SFINAE-selected `get_impl` overloads and `JSONSerializer<ValueType>::from_json`.
- Element access: `at(index)`, `at(key)`, `operator[](index)`, `operator[](key)`, `value(key, default)`, `value(json_pointer, default)`, `front()`, and `back()`.
- Erase and lookup: iterator/range/key/index `erase`, `find`, `count`, and `contains`, including transparent-key and JSON Pointer overloads where enabled.
- Iteration and capacity: `begin`, `end`, `cbegin`, `cend`, reverse iterators, `items()`, deprecated `iterator_wrapper`, `empty`, `size`, and `max_size`.
- Modifiers: `clear`, `push_back`, `operator+=`, `emplace_back`, `emplace`, array `insert`, object range `insert`, `update`, and `swap`.
- Comparisons: equality, inequality, ordering, and optional C++20 three-way comparison, with special handling for cross-number comparisons, NaN, and `discarded` values.
- Text parsing/streaming: `operator<<`, `operator>>`, `parse`, `accept`, and `sax_parse`, gated by `JSON_NO_IO` where appropriate.
- Binary support: `to_cbor`, `to_msgpack`, `to_ubjson`, `to_bjdata`, `to_bson`, and matching `from_*` functions using `binary_writer`, `binary_reader`, and SAX DOM parsers.
- JSON Pointer/Patch/Merge Patch: pointer `operator[]`, pointer `at`, `flatten`, `unflatten`, `patch_inplace`, `patch`, static `diff`, and `merge_patch`.
- Internal storage in this chunk: nested `struct data` owns `value_t m_type` and `json_value m_value`, destroys payloads in its destructor, and disables copying.
- Header tail: `to_string(const basic_json&)`, `operator ""_json`, `operator ""_json_pointer`, `std::hash`, `std::less<value_t>`, optional `std::swap` specialization before C++20, optional global UDL exports, and macro undefinition.

## Control Flow

Lifecycle operations are type-dispatch heavy. The copy constructor copies `m_data.m_type`, checks the source invariant, and switches over `value_t` to deep-copy object, array, string, binary, and scalar payloads. The move constructor moves the storage, then resets the source object to `null` with an empty value so the moved-from object remains destructible and valid. Assignment takes its argument by value, swaps storage and diagnostic positions, assigns the base class, then resets diagnostic parent pointers.

Serialization through `dump` creates a `serializer` around a string output adapter, selects pretty or compact mode based on `indent >= 0`, and delegates all formatting to `serializer::dump`. Stream output follows the same serializer path, using `ostream::width()` as the indentation request and then resetting width to `0`.

Value conversion is selected by template priority tags. The lowest-priority general overload default-constructs a target and calls `JSONSerializer<ValueType>::from_json(*this, ret)`. A higher-priority overload handles non-default-constructible types whose serializer returns the value directly. Further overloads copy or convert to another `basic_json` type, or return an internal pointer. `get()` exposes this selection while rejecting reference targets; references must go through `get_ref()`, which verifies the requested reference type through `get_ptr()`.

Element access separates checked and unchecked semantics. `at()` validates the current type and array bounds or object-key presence, throwing nlohmann exception types with stable error IDs. Non-const `operator[]` converts `null` to an array or object as needed, grows arrays with null values for out-of-range numeric indices, and inserts `nullptr` for missing object keys. Const `operator[]` asserts the key exists rather than inserting.

Mutation APIs generally validate the current JSON kind, sometimes converting `null` to the required container. `push_back` and `emplace_back` convert `null` to array; object-pair `push_back`, `emplace`, and `update` convert `null` to object. Array insertion validates that the insertion iterator belongs to the receiving array and rejects inserting a range from the same container. Object `update` can recursively merge existing object values when `merge_objects` is true.

Comparison uses a macro-generated switch that first compares same-type values, then handles mixed integer/unsigned/float numeric combinations, then treats NaN and `discarded` as unordered. If values are different nonnumeric types, ordering falls back to the `value_t` ordering. C++20 builds may use `operator<=>`; older builds define the six relational friend operators.

Parsing and SAX APIs build `detail::input_adapter` instances from generic input or iterator ranges. JSON text input uses `parser`; binary formats use `binary_reader`. DOM-producing binary parses create a `json_sax_dom_parser`, run SAX parse, and return either the populated result or a `discarded` JSON value when parsing fails without exceptions.

`patch_inplace` validates that the patch document is an array of objects, extracts `"op"` and `"path"` fields, maps the operation string to an internal enum, and applies RFC 6902 operations. `add` resolves the parent pointer and inserts/replaces/appends; `remove` erases from an object or array; `replace` assigns through checked pointer access; `move` reads from `"from"`, removes it, then adds it at the target; `copy` reads from `"from"` and adds; `test` compares the target value and throws if it does not match. `diff` recursively emits a JSON Patch array that transforms source into target. `merge_patch` follows RFC 7386 behavior: object patches recurse, null members erase keys, and non-object patches replace the whole value.

## State and Persistence

All state is local in-memory C++ object state. `basic_json::data` stores the active type tag and union-like `json_value` payload. Heap-allocated payloads for object, array, string, and binary values are owned by the JSON value and destroyed through `json_value::destroy(m_type)` when `data` is destructed. Diagnostic builds also maintain parent pointers and, if enabled, parse start/end positions.

The code performs no WiredTiger persistence and does not read or write database files, logs, metadata, checkpoints, or durable configuration. Persistence-like behavior is limited to serialization into caller-provided strings, streams, output adapters, or vectors, and deserialization from caller-provided inputs.

Mutating APIs can invalidate references, pointers, and iterators. The header documents this explicitly for internal pointers returned by `get_ptr()`/`get()`. Array growth, insertion, erase, and swap can relocate child values; diagnostic parent pointers are repaired with `set_parent` or `set_parents` after such operations.

## Dependencies and Integration Points

- Earlier definitions in the same header: `value_t`, `json_value`, `serializer`, `parser`, `binary_reader`, `binary_writer`, `json_pointer`, iterators, `iteration_proxy`, `byte_container_with_subtype`, exception classes, input/output adapters, and detection traits.
- C++ standard library: containers, iterators, streams, allocator traits, type traits, `std::hash`, `std::less`, `std::partial_ordering` when available, and `std::isnan` for float comparison.
- User customization: conversions rely on `JSONSerializer<ValueType>::from_json`; projects can extend behavior through nlohmann's `from_json`/`to_json` conventions.
- Compile-time configuration macros: `JSON_DIAGNOSTICS`, `JSON_DIAGNOSTIC_POSITIONS`, `JSON_NO_IO`, `JSON_HAS_THREE_WAY_COMPARISON`, `JSON_USE_LEGACY_DISCARDED_VALUE_COMPARISON`, `JSON_USE_GLOBAL_UDLS`, and `JSON_TEST_KEEP_MACROS` materially alter exposed APIs or behavior.
- WiredTiger test integration: this vendored header allows tests under `sources/storage-engines/wiredtiger/test` to use a consistent nlohmann/json version independent of the host environment.
- Namespace integration: the code closes `NLOHMANN_JSON_NAMESPACE`, adds literals in `nlohmann::literals::json_literals`, and specializes selected `std` templates for nlohmann types.

## Risks and Maintenance Notes

- This is vendored third-party code. Local edits risk diverging from upstream nlohmann/json 3.12.0 and should be avoided unless the repository intentionally carries a patch.
- Template overload resolution is delicate. Changes to `get`, `value`, `operator[]`, transparent-key support, or scalar comparison overloads can introduce ambiguous calls or break existing consumer code across C++ standard versions.
- Non-const `operator[]` has side effects: it converts `null` values into containers, grows arrays, and inserts missing object keys. Tests that only intend lookup should use `at`, `find`, `contains`, or `value`.
- Const object `operator[]` asserts the key exists and does not provide runtime checked semantics in the same way as `at`. Misuse can fail assertions or produce undefined behavior depending on build settings.
- Mixed signed/unsigned numeric comparison casts unsigned values to `number_integer_t` in one branch. Very large unsigned values can be sensitive to implementation details and should be covered by upstream tests.
- NaN and `discarded` values are treated as unordered, with legacy behavior optionally controlled by `JSON_USE_LEGACY_DISCARDED_VALUE_COMPARISON`. Test expectations can change with that macro.
- `patch_inplace` mutates the target progressively. If a later patch operation fails, earlier operations remain applied; callers needing all-or-nothing behavior should use `patch()` on a copy.
- Binary deserialization returns `discarded` on parse failure when exceptions are disabled. Callers must check `is_discarded()` if they suppress exceptions.
- Macro cleanup at the end is important for header hygiene. Defining `JSON_TEST_KEEP_MACROS` intentionally leaves some macros visible for tests; otherwise consumers should not rely on those macro names after inclusion.

## Test Signals

Useful validation signals for this chunk include:

- Upstream nlohmann/json unit tests for `basic_json` copy/move/assignment, `dump`, `parse`, `accept`, SAX parsing, binary formats, JSON Pointer, JSON Patch, Merge Patch, iterators, and comparisons.
- WiredTiger test builds that include this vendored header under the repository's supported C++ standard modes.
- Compile-only coverage with and without key feature macros such as `JSON_NO_IO`, `JSON_DIAGNOSTICS`, `JSON_DIAGNOSTIC_POSITIONS`, `JSON_USE_GLOBAL_UDLS`, and C++20 three-way comparison support.
- Runtime tests for checked access and exception IDs: array bounds, missing object keys, wrong-type `at`, wrong-type `erase`, invalid insert iterators, malformed patches, failed patch tests, and parse failures with exceptions disabled.
- Round-trip tests for JSON text and binary encodings: `parse(dump(j))`, `from_cbor(to_cbor(j))`, `from_msgpack(to_msgpack(j))`, `from_ubjson(to_ubjson(j))`, `from_bjdata(to_bjdata(j))`, and `from_bson(to_bson(j))` for representative scalar, object, array, string, binary, and nested values.
- Sanitizer or debug builds that exercise array growth, insertion, erase, swap, move construction, and patch operations, since those paths stress ownership, iterator validity, and diagnostic parent repair.
