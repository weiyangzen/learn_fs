# Research: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucJson.hh

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-007953`: lines 1-6194, `Docs/researches/chunks/subset-b-007953_research.md`
- `subset-b-007954`: lines 6195-13847, `Docs/researches/chunks/subset-b-007954_research.md`
- `subset-b-007955`: lines 13848-21067, `Docs/researches/chunks/subset-b-007955_research.md`
- `subset-b-007956`: lines 21068-25716, `Docs/researches/chunks/subset-b-007956_research.md`

## Chunk Research

### subset-b-007953: lines 1-6194

# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucJson.hh lines 1-6194

## Purpose

This chunk is the opening slice of XRootD's local `XrdOucJson.hh` wrapper for nlohmann/json. If `USE_SYSTEM_NLOHMANN_JSON` is defined, the header delegates to `<nlohmann/json.hpp>`; otherwise it embeds the beginning of the single-header nlohmann/json 3.12.0 amalgamation. The covered range does not yet contain the full `basic_json` class body, parser, serializer, or public aliases at the end of the amalgamation. It establishes the ABI namespace, compiler-feature compatibility layer, type traits, exception classes, and the first `from_json` / `to_json` conversion helpers used later by the public JSON type.

For XRootD, this file is a vendored dependency boundary: code can include one XRootD-owned header and either use the system nlohmann/json package or a fixed bundled implementation with the same API surface. This reduces build-time dependency requirements while preserving a switch for distributions that prefer system libraries.

## Important APIs, Types, And Macros

- `USE_SYSTEM_NLOHMANN_JSON`: build switch at the top of the file. When enabled, all bundled code in this chunk is bypassed and the system nlohmann/json header defines the API.
- `NLOHMANN_JSON_VERSION_MAJOR/MINOR/PATCH`: pins the vendored implementation to `3.12.0` and warns if another nlohmann/json version was already included.
- `NLOHMANN_JSON_NAMESPACE`, `NLOHMANN_JSON_NAMESPACE_BEGIN`, and `NLOHMANN_JSON_NAMESPACE_END`: construct the inline ABI namespace under `nlohmann`, incorporating version and ABI tags for diagnostics, diagnostic byte positions, and legacy discarded-value comparison.
- `JSON_DIAGNOSTICS`, `JSON_DIAGNOSTIC_POSITIONS`, and `JSON_USE_LEGACY_DISCARDED_VALUE_COMPARISON`: compile-time ABI-affecting feature flags. Changing them changes namespace tagging and therefore type/link compatibility.
- `detail::nonesuch`, `detail::detector`, `is_detected`, `detected_t`, `detected_or_t`, `is_detected_exact`, and `is_detected_convertible`: C++11-compatible detection idiom used throughout the rest of the header to enable or suppress overloads by available methods and nested types.
- Hedley-derived `JSON_HEDLEY_*` macros: compiler and feature probes for GCC, Clang, MSVC, Intel, ARM, TI, IBM, SunPro, IAR, etc. They normalize attributes, pragmas, casts, fallthrough annotations, branch prediction, no-return, visibility, deprecation, `nodiscard`, constexpr, inline behavior, diagnostic push/pop, and unsupported compiler checks.
- `JSON_HAS_CPP_11/14/17/20/23/26`, `JSON_HAS_FILESYSTEM`, `JSON_HAS_EXPERIMENTAL_FILESYSTEM`, `JSON_HAS_THREE_WAY_COMPARISON`, `JSON_HAS_RANGES`, and `JSON_HAS_STATIC_RTTI`: local feature macros that conditionally expose optional, filesystem, ranges, and comparison support.
- `JSON_THROW`, `JSON_TRY`, `JSON_CATCH`, `JSON_INTERNAL_CATCH`, and `JSON_ASSERT`: exception and assertion indirection points. With exceptions disabled or `JSON_NOEXCEPTION`, throwing aborts unless the user overrides these macros.
- `NLOHMANN_JSON_SERIALIZE_ENUM`: public macro that generates `to_json` and `from_json` overloads for enum mapping tables.
- `NLOHMANN_DEFINE_TYPE_*` and `NLOHMANN_DEFINE_DERIVED_TYPE_*`: macro families that generate intrusive or non-intrusive object field serialization hooks for user-defined types.
- `detail::value_t`: internal JSON type enum with entries for null, object, array, string, boolean, signed integer, unsigned integer, floating point, binary, and discarded values.
- `detail::replace_substring`, `detail::escape`, and `detail::unescape`: RFC 6901 JSON Pointer token escaping helpers.
- `detail::position_t`: line/column/byte counter structure used by parse errors and SAX-style position reporting.
- `detail::enable_if_t`, `index_sequence`, `make_index_sequence`, `priority_tag`, `static_const`, and `make_array`: C++11/C++14 compatibility utilities used to keep the library usable across older toolchains.
- `json_fwd.hpp` declarations: forward-declare `adl_serializer`, `basic_json`, `json_pointer`, `ordered_map`, and aliases `json` / `ordered_json`.
- `detail::exception`, `parse_error`, `invalid_iterator`, `type_error`, `out_of_range`, and `other_error`: nlohmann/json exception hierarchy with stable numeric `id` fields and formatted `what()` messages.
- `detail::from_json` overload set and `detail::to_json` overload set: conversion functions for primitives, strings, arrays, objects, tuples, pairs, C arrays, optional values, filesystem paths, valarrays, maps with non-string keys, and enum values.
- `detail::from_json_fn` / `detail::to_json_fn` and inline `nlohmann::from_json` / `nlohmann::to_json` function objects: ADL-friendly dispatch objects used by `adl_serializer` and `basic_json::get`.
- `detail::iteration_proxy_value` and `detail::iteration_proxy`: helper backing `items()` iteration, including structured binding support via `std::tuple_size` and `std::tuple_element` specializations.
- `detail::external_constructor<value_t::...>` specializations: low-level constructors that mutate `basic_json` storage for booleans, strings, binary values, numbers, arrays, and objects.

## Control Flow

The first control-flow decision is purely preprocessor-driven. `USE_SYSTEM_NLOHMANN_JSON` includes the system header and skips the bundled implementation. Otherwise, the file enters the nlohmann/json include guard and starts expanding embedded logical headers in the same order as the upstream amalgamation.

Within the bundled path, the setup flow is:

1. Define version and ABI namespace macros, including ABI tag components selected by diagnostics-related flags.
2. Include standard-library headers required by early conversion, exception, and meta-programming code.
3. Define the detection idiom and Hedley portability macros.
4. Validate compiler support unless `JSON_SKIP_UNSUPPORTED_COMPILER_CHECK` is defined.
5. Detect C++ language/library features and configure exception/assertion indirection.
6. Define serialization helper macros for enum and user-defined type mappings.
7. Define `value_t`, JSON Pointer string escaping, token position state, and C++ compatibility helpers.
8. Forward-declare the public JSON templates and aliases.
9. Define type traits that choose later overloads for arrays, objects, strings, maps, iterators, JSON pointers, transparent object keys, enum conversions, integer range checks, and user-provided ADL serializers.
10. Define exception classes and conversion helpers.

Runtime control flow in this chunk appears mostly in conversion helpers:

- `from_json` verifies the stored JSON type with predicates such as `is_null()`, `is_string()`, `is_array()`, `is_object()`, `is_binary()`, and `is_boolean()`. Type mismatches throw `detail::type_error::create(302, ...)`.
- Numeric extraction uses `get_arithmetic_value`, switching on `value_t` and reading the correct stored numeric pointer. General arithmetic conversions also accept boolean input, while the explicit numeric template parameters do not.
- Array extraction uses overload priority. Native `array_t` copies directly; `std::array` and C arrays use indexed `at()` access; containers with `reserve()` allocate once then insert transformed elements; other insertable containers fall back to inserter-based population.
- Object extraction checks that the JSON value is an object, iterates the internal `object_t`, converts each mapped value, and inserts into the requested object-like container. Maps/unordered maps with non-string keys are represented as arrays of two-element arrays.
- Tuple and pair extraction treats JSON arrays as positional tuples, using `index_sequence` to call `at(N).get<T>()`.
- `to_json` selects a constructor path through SFINAE. Primitive values call the matching `external_constructor`, compatible ranges become arrays, compatible object types become objects, tuples and pairs become arrays, optional empty values become null, and filesystem paths become UTF-8 strings when filesystem support is enabled.
- `external_constructor` specializations always destroy the old `basic_json` union member before assigning the new type, then reset parent pointers for arrays/objects when diagnostics need parent tracking.

## State And Persistence Behavior

This chunk does not persist application data and does not perform I/O. Its state is compile-time configuration and in-memory JSON object mutation.

The relevant persistent contract is ABI and source compatibility. The inline namespace is versioned as `json_abi..._v3_12_0` unless disabled by macros. Diagnostics-related flags are part of the namespace tag, so object files compiled with different settings can refer to different nlohmann/json types. The `USE_SYSTEM_NLOHMANN_JSON` path is another compatibility boundary: the actual implementation and bug behavior can differ from the vendored 3.12.0 copy if the system package is a different release.

The runtime state touched in this range is `basic_json`'s internal `m_data.m_type` and `m_data.m_value`, though the full class is defined later. `external_constructor` functions explicitly destroy the existing value before replacing it, preserving memory ownership for heap-backed strings, arrays, objects, and binary values. Array/object construction calls `set_parents()` or `set_parent()` so diagnostic paths can be reconstructed when `JSON_DIAGNOSTICS` is enabled.

Exceptions store formatted messages inside a `std::runtime_error` member. `parse_error` additionally persists a byte position. With `JSON_DIAGNOSTIC_POSITIONS`, exception formatting can include start/end byte ranges from the leaf JSON element.

## Dependencies

The covered range depends only on the C++ standard library and optional compiler/library features. It includes or conditionally references algorithms, arrays, maps, unordered maps, forward lists, valarrays, vectors, tuples, strings, memory, iterators, type traits, exceptions, limits, cstddef/cstdint, filesystem or experimental filesystem, optional, compare, ranges, and string view.

The code also embeds third-party Hedley compatibility macros and a small Abseil-derived C++11 `integer_sequence` replacement. These are header-local compatibility dependencies rather than linked libraries.

If `USE_SYSTEM_NLOHMANN_JSON` is active, the dependency moves to the system-provided nlohmann/json installation. That can affect available APIs, namespace versioning, warnings, defects, and transitive standard-library requirements.

## Integration Points

- XRootD source code includes this header as the project-local JSON API. Downstream users see nlohmann/json names, not XRootD-specific wrapper types.
- Build systems and packagers can choose bundled versus system nlohmann/json by defining or omitting `USE_SYSTEM_NLOHMANN_JSON`.
- User code can provide ADL `to_json` / `from_json` overloads or specialize `adl_serializer`; the traits in this chunk are what discover those hooks.
- User code can opt into enum/object serialization macros defined here, which generate overloads in the surrounding namespace.
- Later parts of the same header depend on `value_t`, exception types, type traits, `external_constructor`, and conversion functions when implementing `basic_json` constructors, `get`, parser errors, iterators, JSON Pointer, serialization, and binary formats.
- Filesystem integration is conditional. When detected, `std::filesystem::path` or `std::experimental::filesystem::path` converts to/from UTF-8 JSON strings.
- `items()` integration is partly defined here through `iteration_proxy`, including support for structured bindings like `for (auto& [key, value] : j.items())`.

## Risks And Maintenance Notes

- Vendored/system divergence is the central risk. The bundled code is 3.12.0, but `USE_SYSTEM_NLOHMANN_JSON` can select another version with different overload resolution, diagnostics, bug fixes, or ABI namespace tags.
- ABI-affecting macros must be consistent across all translation units. Mixing `JSON_DIAGNOSTICS`, `JSON_DIAGNOSTIC_POSITIONS`, `JSON_USE_LEGACY_DISCARDED_VALUE_COMPARISON`, or namespace-version settings can create incompatible JSON types.
- `JSON_NOEXCEPTION` changes failure behavior from throwing typed exceptions to `std::abort()` unless user macros replace `JSON_THROW`. XRootD code that expects parse/type errors to be recoverable must ensure exceptions are enabled or overridden appropriately.
- Numeric conversions in `from_json` use `static_cast` after selecting numeric storage. Some narrowing, sign, and floating/integer conversions are permitted by design and may not report overflow.
- Object/array conversion is heavily SFINAE-driven. New custom containers can be classified unexpectedly if they expose `begin`/`end`, `mapped_type`, `key_type`, `value_type`, transparent comparators, or string-like constructors.
- `std::map` and `std::unordered_map` with non-string keys serialize as arrays of pairs, not JSON objects. Consumers expecting object syntax can break when key types change from string-like to non-string-like.
- The exception diagnostic path walks parent pointers and object/array contents. Parent tracking must stay correct after any future edits to constructors or mutation paths.
- The header specializes `std::tuple_size` and `std::tuple_element` for `iteration_proxy_value`, which is allowed for user-defined types but sensitive to namespace and include-order issues.
- Compiler compatibility macros are broad and old-toolchain-oriented. Local edits to this region are risky because small macro changes can affect every downstream overload, warning state, or language-feature branch.

## Test Signals

Useful signals for this chunk are compile- and behavior-oriented:

- Build XRootD both with the bundled header and with `USE_SYSTEM_NLOHMANN_JSON` against the supported system nlohmann/json package.
- Compile translation units that include `XrdOucJson.hh` under the project's minimum and common modern C++ standards to exercise `JSON_HAS_CPP_*` branches.
- Exercise JSON parsing/getting paths that throw `parse_error`, `type_error`, and `out_of_range`, confirming exception IDs and messages remain compatible with callers.
- Round-trip primitive values, strings, binary values, vectors, maps, unordered maps, pairs, tuples, `std::array`, C arrays, enums, optional values, and filesystem paths where enabled.
- Verify `items()` iteration and structured bindings over arrays, objects, and primitive values.
- Run builds with diagnostics toggles if XRootD supports them, because those flags affect both exception content and ABI namespace selection.
- Watch for compiler warnings around this header after toolchain upgrades; the Hedley and diagnostic suppression blocks are intended to keep header-only use quiet across many compilers.

### subset-b-007954: lines 6195-13847

# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucJson.hh lines 6195-13847

## Scope

This chunk covers the middle of XRootD's vendored `nlohmann/json` 3.12.0 single-header implementation. The assigned range starts at the `adl_serializer` definition, then includes binary subtype support, JSON hashing, input adapters, the JSON lexer, SAX interfaces and DOM-building SAX handlers, binary readers for BSON/CBOR/MessagePack/UBJSON/BJData, the recursive-descent JSON text parser, and the beginning of iterator support.

This is not XRootD-specific application code. Its integration role is to provide the `nlohmann::json` API that XRootD includes through `XrdOucJson.hh`, with an escape hatch at the top of the file to use the system `nlohmann/json.hpp` instead when `USE_SYSTEM_NLOHMANN_JSON` is defined.

## Purpose

The code in this chunk is the parsing and traversal core for JSON values. It lets callers:

- customize conversion to and from user types through argument-dependent `to_json` and `from_json`;
- represent binary JSON values with optional numeric subtypes;
- hash JSON values for use in standard unordered containers;
- adapt many input sources into a uniform byte stream;
- tokenize JSON text, validate UTF-8, decode escapes, and classify numeric tokens;
- drive SAX consumers for validation-only parsing, DOM construction, or callback-filtered DOM construction;
- parse binary encodings into the same SAX event stream;
- expose iterator primitives used by `basic_json::iterator` and `const_iterator`.

For XRootD consumers, the practical effect is that configuration or protocol code using `nlohmann::json` can parse strings, streams, byte buffers, CBOR/MessagePack/UBJSON/BJData/BSON data, and then traverse or convert the resulting DOM with upstream-compatible behavior.

## Important APIs, Types, and Functions

- `nlohmann::adl_serializer<ValueType>` at lines 6197-6230 forwards conversion to free `::nlohmann::from_json` and `::nlohmann::to_json` overloads. This is the default customization hook used by `basic_json::get<T>()` and assignment/construction from arbitrary types.
- `byte_container_with_subtype<BinaryType>` at lines 6254-6336 extends a byte container with `subtype_type`, `set_subtype`, `subtype`, `has_subtype`, and `clear_subtype`. The sentinel for "no subtype" is returned as all-ones `uint64_t`, while `m_has_subtype` records whether that sentinel is meaningful.
- `detail::combine` and `detail::hash` at lines 6370-6474 implement recursive JSON hashing. The value type is included in the seed so `null`, `false`, signed zero-like numbers, unsigned values, strings, arrays, objects, and binary blobs do not collapse solely by payload.
- `detail::input_format_t` at line 6549 identifies supported input encodings: JSON, CBOR, MessagePack, UBJSON, BSON, and BJData.
- Input adapters at lines 6555-7056 normalize sources. They include `file_input_adapter`, `input_stream_adapter`, `iterator_input_adapter`, wide-string adapters, container/pointer/array overloads for `input_adapter`, and `span_input_adapter`.
- `detail::lexer_base` and `detail::lexer` begin at lines 7122 and 7198. They define token kinds, token names, source positions, string and number buffers, and scanner methods such as `scan_string`, `scan_comment`, `scan_number`, and `scan`.
- `json_sax<BasicJsonType>` at lines 8738-8859 is the abstract event interface: scalar events, `start_object`, `key`, `end_object`, `start_array`, `end_array`, and `parse_error`.
- `detail::json_sax_dom_parser` at lines 8881-9185 turns SAX events into a `BasicJsonType` DOM by maintaining a stack of object/array pointers.
- `detail::json_sax_dom_callback_parser` at lines 9187-9622 adds `parser_callback_t` filtering, with keep stacks for values and object keys and a discarded sentinel for skipped content.
- `detail::json_sax_acceptor` at lines 9624-9698 is a validation-only SAX target that returns true for valid events and false on parse errors.
- SAX trait utilities at lines 9733-9892 detect whether a user SAX type implements the required methods with compatible return types.
- `detail::binary_reader<BasicJsonType, InputAdapterType, SAX>` at lines 9910-12914 converts BSON, CBOR, MessagePack, UBJSON, and BJData byte streams to SAX events.
- `detail::parser<BasicJsonType, InputAdapterType>` at lines 12996-13469 parses JSON text tokens from the lexer and drives a SAX target.
- `detail::primitive_iterator_t`, `detail::internal_iterator`, and the start of `detail::iter_impl` at lines 13517-13847 provide the storage and constructor logic for iterating primitive, array, and object JSON values.

## Control Flow

Text JSON parsing starts by adapting the input with `detail::input_adapter`, constructing a `lexer`, and then constructing a `parser`. `parser::parse` selects either `json_sax_dom_parser` or `json_sax_dom_callback_parser` depending on whether a callback was supplied. `parser::accept` uses `json_sax_acceptor` for validation. `parser::sax_parse` drives a caller-provided SAX target.

`parser::sax_parse_internal` is an iterative recursive-descent state machine. It reads an initial token, emits a scalar, object-start, or array-start event, and pushes `false` for objects or `true` for arrays onto a state stack. After each value it evaluates the enclosing state: arrays accept commas and `]`; objects accept commas, string keys, colons, values, and `}`. Strict mode requires end-of-input after the top-level value. `ignore_trailing_commas` allows `,]` and `,}` in the state-evaluation branches.

Lexing is split by token class. `scan_string` validates RFC 8259 strings, handles standard escapes, decodes `\u` sequences including surrogate pairs, rejects unescaped control characters, and validates multibyte UTF-8 byte ranges. `scan_number` uses an explicit finite state machine with labels to enforce JSON number grammar, accumulates the token text, then classifies it as signed integer, unsigned integer, or floating point. `scan_comment` is available only when the parser is configured to ignore comments, and handles `//` and `/* ... */` comments.

DOM construction is event-driven. `json_sax_dom_parser::handle_value` assigns the root when the stack is empty, appends to the current array, or writes through `object_element` for the most recent key. Object and array starts push pointers onto `ref_stack`; matching ends set parent pointers and pop the stack. The callback parser uses the same shape, but first calls the callback at object/array starts, keys, values, and object/array ends, then removes or replaces discarded values as needed.

Binary parsing starts in `binary_reader::sax_parse`, which dispatches by `input_format_t`. BSON validates document sizes, reads NUL-terminated keys, and emits typed values for double, string, object, array, binary, boolean, null, integer, and integer64 records. CBOR dispatches on the initial major-type byte and supports unsigned/negative integers, byte strings, UTF-8 strings, arrays, maps, tags, booleans, null, and half/single/double precision floats. MessagePack similarly switches on prefix families for fixints, fixmap, fixarray, fixstr, bin/ext, float, integer, array, and map encodings. UBJSON/BJData parse marker-based values, optimized containers with optional size/type markers, high-precision numbers, and BJData ND-array metadata.

Iterator construction in this chunk is type-directed. `iter_impl(pointer object)` records the owning JSON pointer, initializes an object iterator for objects, an array iterator for arrays, and a `primitive_iterator_t` for all scalar, null, binary, and discarded values. The actual navigation operators continue after this chunk.

## State And Persistence Behavior

This chunk owns no XRootD persistent state. It is header-only library code whose runtime state is stack or object-local during parse/conversion/traversal.

Important transient state includes:

- input adapter cursor state, such as `FILE*`, `std::streambuf*`, iterator pairs, or wide-string UTF-8 buffers;
- lexer state: current character, unget flag, source position, raw token text, decoded token buffer, numeric values, decimal separator, and error message pointer;
- parser state: last token, SAX callback pointer, lexer instance, exception policy, and trailing-comma policy;
- DOM SAX state: root reference, `ref_stack`, current `object_element`, error flag, exception policy, and optional lexer pointer for diagnostic positions;
- callback parser state: `keep_stack`, `key_keep_stack`, and a reusable discarded JSON value;
- binary reader state: current byte, bytes-read count, selected format, endian flag, SAX pointer, and BJData lookup tables.

For persistence, the notable behavior is format compatibility rather than file storage. Binary readers interpret on-wire encodings and produce JSON DOM state. `get_number` swaps numeric byte order depending on host endianness and format: CBOR, MessagePack, and UBJSON use network order, while BSON and BJData are treated as little-endian. CBOR tags can be rejected, ignored, or stored as binary subtypes depending on `cbor_tag_handler_t`.

With `JSON_DIAGNOSTIC_POSITIONS`, DOM SAX parsers also record start and end offsets into JSON values. That state is embedded in parsed values and depends on lexer position accounting, token lengths, and the special object/array start/end handling in the SAX handlers.

## Dependencies And Integration Points

- The chunk depends on the earlier parts of the same header for ABI namespace macros, exception types, `value_t`, type traits, `char_traits`, `position_t`, string concatenation helpers, endian detection, and `BasicJsonType` internals.
- It depends on standard C and C++ headers including `<cstdio>`, `<cstring>`, `<istream>`, `<streambuf>`, `<iterator>`, `<memory>`, `<limits>`, `<cmath>`, `<array>`, `<vector>`, `<string>`, `<tuple>`, `<functional>`, and `<type_traits>`.
- `JSON_NO_IO` removes `FILE*` and `std::istream` adapter support. `USE_SYSTEM_NLOHMANN_JSON` bypasses this vendored body entirely at the top of `XrdOucJson.hh`.
- Public `basic_json` methods later in the file use these internals for `parse`, `accept`, `sax_parse`, `from_cbor`, `from_msgpack`, `from_ubjson`, `from_bjdata`, and `from_bson`.
- Standard library integration later in the full header uses `detail::hash` to specialize `std::hash<nlohmann::json>`.
- XRootD integration is broad and compile-time: any source including `XrdOucJson.hh` obtains this `nlohmann` namespace implementation unless the build chooses the system header. Therefore ABI macro settings and the vendored version must be consistent across translation units.

## Risks And Edge Cases

- This is a vendored third-party header. Local edits risk diverging from upstream `nlohmann/json` behavior and can be hard to reconcile with builds that define `USE_SYSTEM_NLOHMANN_JSON`.
- `adl_serializer` intentionally forwards to free functions with ADL. User-defined conversions can become ambiguous or surprising if multiple `to_json`/`from_json` overloads are visible.
- `byte_container_with_subtype::subtype()` returns all-ones when no subtype is present; callers must check `has_subtype()` instead of treating that value as a real subtype.
- `detail::hash` recurses through all arrays and objects. It is deterministic for a given object ordering but can be expensive for large JSON trees and inherits collision behavior from `std::hash` for strings and numbers.
- `input_stream_adapter` reads through `streambuf` directly and adjusts only EOF state. Code that expects normal `istream` formatted-extraction state transitions may be surprised after parsing.
- Iterator and pointer input adapters depend on lifetime of the underlying data. Passing temporary buffers through low-level adapter paths can produce dangling reads if wrappers are misused.
- String lexing is strict about UTF-8 and control characters. Inputs with comments, unescaped control bytes, malformed surrogate pairs, overlong UTF-8, or invalid continuation bytes will produce parse errors unless the relevant nonstandard parser option is enabled for comments.
- Number scanning uses locale-aware C conversion after replacing or tracking the decimal point, and returns parse errors or falls back between signed, unsigned, and float classifications at numeric limits. Boundary values around `int64_t`, `uint64_t`, NaN, infinity, and decimal/exponent forms are high-value test cases.
- Callback parsing mutates the partially built DOM while callback decisions are made. Incorrect assumptions about callback depth, discarded sentinels, or object key filtering can lead to missing values that are intentional rather than parser corruption.
- `json_sax_dom_parser` and callback parser reach into `BasicJsonType::m_data` internals for performance. That tight coupling means custom `BasicJsonType` specializations must preserve the expected internals.
- Binary format readers trust declared lengths enough to loop and append until EOF or memory pressure. Length fields near `SIZE_MAX`, deeply nested containers, and indefinite-length encodings are important denial-of-service surfaces.
- BJData ND-array support multiplies dimensions and includes explicit overflow checks. Regressions here could wrap array sizes, emit malformed JData annotations, or allow recursive ND arrays, which the current code rejects.
- Binary object formats require string keys. CBOR maps and MessagePack maps are parsed through string-key helpers in this implementation; non-string map keys are not accepted as object keys.
- `get_to` advances `chars_read` specially on short primitive reads to report the failing location. Error positions in binary readers can shift if this accounting is changed.
- The beginning of `iter_impl` asserts that iterators are initialized with a non-null JSON pointer and chooses storage based on the value type at construction. Mutating a JSON value while iterators are live remains subject to the library's usual invalidation rules.

## Test Signals

Useful signals for this chunk are mostly upstream `nlohmann/json` conformance tests or XRootD tests that exercise JSON configuration parsing:

- ADL conversion tests should cover in-place `from_json(j, T&)`, value-returning `from_json(j, identity_tag<T>)`, and `to_json(j, T)` overload resolution.
- Binary JSON tests should cover subtype set/clear/equality, CBOR tag handling modes, and `std::hash` behavior for binary values with and without subtypes.
- Input adapter tests should parse from `std::string`, C strings, byte vectors, iterators, arrays, `FILE*`, `std::istream`, and UTF-16/UTF-32 sources when enabled.
- JSON text parser tests should cover empty input, strict trailing data rejection, allowed/forbidden trailing commas, optional comments, every scalar token, nested arrays/objects, missing separators, and meaningful parse-error positions.
- UTF-8 and escape tests should include all control characters, valid and invalid `\u` escapes, valid surrogate pairs, isolated high/low surrogates, overlong byte forms, truncated multibyte sequences, and maximum code point `U+10FFFF`.
- Numeric tests should include `-0`, signed and unsigned 64-bit boundaries, overflow to floating point, malformed exponent/decimal forms, locale decimal separators, nonfinite float rejection where applicable, and raw token retention for `number_float`.
- SAX tests should verify callback filtering at keys, values, object starts/ends, and array starts/ends, plus validation-only `accept` behavior with `allow_exceptions` both true and false.
- Binary reader tests should cover BSON document length validation, CBOR indefinite strings/binaries/arrays/maps, MessagePack fix and extended forms, UBJSON optimized arrays/objects, BJData unsigned markers, high-precision numbers, ND-array conversion to `_ArrayType_`, `_ArraySize_`, and `_ArrayData_`, and EOF in the middle of primitive reads.
- Iterator tests for the visible portion should verify begin/end setup for primitive, array, and object values once the later iterator methods are included.
- Build tests should compile with and without `JSON_NO_IO`, with `USE_SYSTEM_NLOHMANN_JSON`, and across compilers with different endian and byteswap support to ensure this vendored header and the system-header path remain behaviorally compatible enough for XRootD.

### subset-b-007955: lines 13848-21067

# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucJson.hh lines 13848-21067

## Scope

This chunk is a large middle section of XRootD's vendored, single-header copy of `nlohmann::json` version 3.12.0. It starts in the tail of `detail::iter_impl` and continues through reverse iteration, JSON Pointer support, output adapters, binary serialization, floating-point-to-text conversion, text serialization, `ordered_map`, and the beginning of `basic_json` storage and constructors.

The code is generic library infrastructure rather than XRootD-specific policy. Its observable role in this tree is to provide the JSON value type, JSON Pointer access, dump/binary serialization, ordered-object option, and internal storage model used by any XRootD code that includes `XrdOucJson.hh`.

## Purpose

The chunk implements the runtime mechanics that make `basic_json` behave like an STL-style container and a JSON serialization engine:

- iterator dereference, motion, comparison, indexing, object-key access, and reverse iteration;
- RFC 6901 JSON Pointer parsing, token escaping, pointer traversal, `flatten`, and `unflatten`;
- `json_ref`, the initializer-list helper that lets `basic_json` distinguish owned temporaries from referenced values;
- output abstraction over vectors, strings, and streams;
- binary output for BSON, CBOR, MessagePack, UBJSON, and BJData;
- shortest round-trippable decimal conversion for floating point values plus textual JSON dumping;
- `ordered_map`, a vector-backed object container preserving insertion order for `ordered_json`;
- `basic_json` aliases, allocator-backed union storage, parent-pointer diagnostics, and the first constructors.

This is a header-only implementation section. Most functions are templates or inline class members, so compile-time integration and macro configuration matter as much as normal link-time behavior.

## Important APIs, Types, And Functions

### Iterator Infrastructure

The opening lines finish `detail::iter_impl<BasicJsonType>`. `set_begin()` and `set_end()` dispatch on `m_object->m_data.m_type` and initialize the active member in `m_it`:

- objects use `object->begin()` / `object->end()`;
- arrays use `array->begin()` / `array->end()`;
- `null` has an empty primitive iterator range;
- primitive non-null values expose a single synthetic element.

The public operators implement the user-facing iterator API:

- `operator*()` and `operator->()` return object values, array elements, or the primitive JSON value when the primitive iterator is at begin; otherwise they throw `invalid_iterator.214`.
- `operator++`, `operator--`, `operator+=`, `operator-=`, arithmetic, distance, and `operator[]` advance either object/array iterators or the synthetic primitive iterator.
- object iterators reject random-access ordering and offsets with `invalid_iterator.208`, `.209`, or `.213`.
- `operator==` rejects comparisons across different containers with `invalid_iterator.212`, while value-initialized iterators compare equal.
- `key()` is valid only for object iterators; `value()` delegates to `operator*()`.

`json_reverse_iterator<Base>` wraps `std::reverse_iterator<Base>` but preserves JSON-specific `key()` and `value()` by decrementing the base iterator before reading. It is the backing type for `basic_json::reverse_iterator` and `const_reverse_iterator`.

### Base-Class Customization

`detail::json_default_base` and `json_base_class<T>` normalize the `CustomBaseClass` template parameter. `basic_json` always derives from some base class: an empty default when `CustomBaseClass == void`, otherwise the supplied type. This lets constructors and assignments avoid case splits for "no base class" versus "custom base class."

### JSON Pointer

`json_pointer<RefStringType>` stores `reference_tokens` as a `std::vector<string_t>`, where `string_t` is either the provided string type or the `StringType` from a `basic_json` template argument for backward compatibility.

Public pointer APIs include:

- constructor from pointer string, parsed by `split`;
- `to_string()` and deprecated string conversion;
- stream output when IO is enabled;
- `operator/=` and `operator/` for appending another pointer, an unescaped string token, or an array index;
- `parent_pointer()`, `pop_back()`, `back()`, `push_back()`, and `empty()`;
- equality, inequality, ordering, and optional C++20 three-way comparison.

Private traversal helpers are the important integration surface with `basic_json`:

- `array_index<BasicJsonType>()` validates array index strings, rejects leading zeroes, non-numeric tokens, overflow, and values beyond `size_type`.
- `get_and_create()` builds missing object/array paths for `unflatten`; a null value becomes an array only for token `"0"`, otherwise an object.
- mutable `get_unchecked()` creates missing values for `operator[]`-style pointer access; null nodes become arrays for numeric tokens or `"-"` and objects otherwise.
- mutable and const `get_checked()` use `at()` and throw for unresolved paths or the special `"-"` array token.
- `contains()` walks without throwing for normal misses, validates token syntax, and rejects unresolved primitive paths.
- `flatten()` recursively emits a pointer-keyed object; empty arrays and objects flatten to `null`.
- `unflatten()` requires an object whose values are primitive, then assigns each value through `json_pointer(element.first).get_and_create(result)`.

The `split()` routine enforces RFC 6901 syntax: a non-empty pointer must start with `/`, and `~` escapes must be only `~0` or `~1`.

### Initializer References

`detail::json_ref<BasicJsonType>` supports initializer-list construction without unnecessary copies. It either owns a `BasicJsonType` or points at an existing const value. It is movable only, has deleted copy assignment/copy construction, and exposes:

- `moved_or_copied()` for constructors to consume owned temporaries or copy referenced values;
- `operator*()` and `operator->()` for type-deduction checks in initializer-list construction.

### Output Adapters

The output layer abstracts where serialized bytes/chars go:

- `output_adapter_protocol<CharType>` is a virtual interface with `write_character` and `write_characters`.
- `output_vector_adapter`, `output_stream_adapter`, and `output_string_adapter` write to `std::vector`, `std::basic_ostream`, and `std::basic_string`.
- `output_adapter` wraps concrete adapters in `std::shared_ptr<output_adapter_protocol<CharType>>`.

This layer is shared by text dumping and binary writers. It hides destination-specific append mechanics while keeping serialization code expressed as sequential writes.

### Binary Writer

`detail::binary_writer<BasicJsonType, CharType>` serializes `basic_json` to multiple binary encodings through an `output_adapter_t<CharType>`.

Public entry points:

- `write_bson()` accepts only top-level objects and throws `type_error.317` otherwise.
- `write_cbor()` recursively emits CBOR major types for null, bool, signed/unsigned integers, floats, strings, arrays, binary, objects, and binary subtypes/tags.
- `write_msgpack()` recursively emits MessagePack fix/int/str/bin/array/map/ext encodings with length-class selection.
- `write_ubjson()` emits UBJSON or BJData depending on flags, including optimized `$` type and `#` count prefixes.

Important private helpers:

- BSON sizing/writing: `calc_bson_entry_header_size`, `calc_bson_*_size`, `write_bson_*`, `write_bson_element`, and `write_bson_object`.
- format prefix selection: `get_cbor_float_prefix`, `get_msgpack_float_prefix`, `get_ubjson_float_prefix`, and `ubjson_prefix`.
- numeric UBJSON emission: `write_number_with_ubjson_prefix` overloads for unsigned, signed, and floating values, including BJData-only unsigned prefixes and high-precision fallback.
- `write_bjdata_ndarray()` detects JData-style objects with `_ArrayType_`, `_ArraySize_`, and `_ArrayData_`, validates total element count, and writes BJData optimized ndarray payloads.
- `write_number()` copies numeric bytes into an array, reverses based on system endianness versus target endianness, and writes raw bytes.
- `write_compact_float()` chooses single-precision output for finite values exactly representable as `float`, otherwise double.
- `to_char_type()` overloads safely convert `std::uint8_t` to signed or unsigned `CharType`.

### Float-To-Text Conversion

The `detail::dtoa_impl` namespace implements Grisu2 for shortest decimal output of finite IEEE single/double values:

- `reinterpret_bits` copies bit representations.
- `diyfp` models a significand and exponent with subtraction, multiplication, normalization, and normalization to a target exponent.
- `compute_boundaries()` finds the lower/upper rounding boundaries for positive finite values.
- `cached_power` and `get_cached_power_for_binary_exponent()` supply powers of ten for scaling.
- digit generation and rounding functions produce a shortest decimal digit buffer that round-trips.
- `append_exponent()` and `format_buffer()` turn the raw digit buffer and decimal exponent into JSON/`%g`-style text.
- `detail::to_chars()` handles sign, zero, finite assertions, Grisu2 invocation, and final formatting.

This is used by text serialization for IEEE `float` and `double`-like `number_float_t` values.

### Text Serializer

`detail::error_handler_t` controls invalid UTF-8 behavior:

- `strict` throws;
- `replace` writes replacement characters;
- `ignore` skips invalid sequences.

`detail::serializer<BasicJsonType>` owns the output adapter, locale metadata, reusable numeric/string buffers, indentation state, and error-handler setting. Its primary API is `dump(val, pretty_print, ensure_ascii, indent_step, current_indent)`.

`dump()` dispatches by `value_t`:

- objects and arrays recurse with optional indentation and comma management;
- strings call `dump_escaped`;
- binary values are represented as JSON objects with `"bytes"` and `"subtype"`;
- booleans, null, discarded values, signed/unsigned integers, and floats use specialized emission paths.

`dump_escaped()` decodes UTF-8 using a DFA, escapes JSON control characters, optionally escapes non-ASCII as `\uXXXX`, emits surrogate pairs for non-BMP code points, and applies the selected invalid UTF-8 policy.

Numeric helpers include:

- `dump_integer()`, with a two-digit lookup table for fast integer-to-decimal conversion;
- `remove_sign()` to handle signed minimum values without undefined overflow;
- `dump_float()`, which emits non-finite values as JSON `null`, uses Grisu2 for IEEE single/double, and falls back to `snprintf("%.*g")` for other float types while normalizing locale decimal points and removing thousands separators.

### Ordered Map

`nlohmann::ordered_map<Key, T, IgnoredLess, Allocator>` is a vector-backed, map-like container preserving insertion order. It derives from `std::vector<std::pair<const Key, T>, Allocator>` and provides:

- `emplace`, `insert`, and `operator[]` that reuse existing keys instead of adding duplicates;
- `at`, `find`, and `count`;
- key and iterator erasure;
- transparent key lookup when C++14 support is enabled.

Because keys are `const` inside `std::pair<const Key, T>`, erase operations destroy and reconstruct vector elements in place to shift elements. This design is compact and preserves insertion order, but lookups and erases are linear.

### `basic_json` Beginning

The chunk starts the main `basic_json` class template. It declares friend access for `json_pointer`, parser, serializer, iterators, binary reader/writer, SAX DOM parsers, and exceptions. It defines core aliases:

- internal aliases for lexer, parser, iterator, reverse iterator, output adapter, binary reader/writer, and serializer;
- public aliases for `value_t`, `json_pointer`, `json_serializer`, `error_handler_t`, `cbor_tag_handler_t`, `bjdata_version_t`, `initializer_list_t`, `input_format_t`, `json_sax_t`;
- exception aliases: `exception`, `parse_error`, `invalid_iterator`, `type_error`, `out_of_range`, `other_error`;
- container aliases: `value_type`, references, `difference_type`, `size_type`, allocator, pointers, iterators.

`meta()` builds a JSON object reporting library name, version, URL, platform, compiler family/version, and C++ standard value.

Storage setup includes:

- type aliases for object, array, string, boolean, integer, unsigned, float, binary, and comparator types;
- allocator-backed `create<T>(Args&&...)`;
- `json_value`, a union holding pointers for object/array/string/binary and inline primitive values for booleans and numbers;
- `json_value(value_t)` default construction for each JSON type;
- typed constructors for strings, objects, arrays, and binary containers;
- `destroy(value_t)`, which first flattens nested arrays/objects into a heap stack before deallocating to avoid recursive destructor depth, then destroys/deallocates the active pointer member.

The `assert_invariant()` helper checks that structured/string/binary pointer members are non-null for their active type and, under `JSON_DIAGNOSTICS`, validates parent pointers. `set_parents()`, range `set_parents()`, and `set_parent()` maintain diagnostic parent links, with special handling for array capacity changes and vector-backed `ordered_json` objects.

The constructor section begins with:

- `basic_json(value_t)` for empty typed values;
- `basic_json(nullptr_t)` for null;
- a compatible-type forwarding constructor using `JSONSerializer<U>::to_json`;
- a cross-`basic_json` constructor that converts by active type and optionally copies diagnostic positions;
- the start of initializer-list construction, where a list of two-element arrays with string first elements is detected as an object.

## Control Flow

Iterator operations are all type-dispatch flows: inspect `m_object->m_data.m_type`, then operate on the matching internal iterator. Invalid combinations are rejected immediately. Primitive values use `primitive_iterator_t` to synthesize a one-element range, so generic algorithms can iterate over primitive JSON values consistently.

JSON Pointer construction first tokenizes the pointer string. Access flows then iterate token by token:

1. Validate or interpret the current token as an object key, array index, or the special `"-"` append marker where permitted.
2. Dispatch on the current JSON node type.
3. For unchecked mutable access, create objects or arrays from null nodes as needed.
4. For checked/const access, call `at()` and throw if the path cannot be resolved.
5. Return the final JSON reference, boolean containment result, or throw a typed exception.

Flattening is recursive over source structure and writes into a result object keyed by pointer strings. Unflattening reverses that by iterating the flattened object, parsing each key as a pointer, creating the path in a result JSON value, and assigning the primitive leaf.

Serialization control flow is also type-dispatch oriented:

- text serialization recurses through object/array members and writes tokens directly to the output adapter;
- binary serialization recurses through values while choosing size prefixes and numeric encodings based on each output format;
- float formatting routes finite IEEE values through Grisu2 and non-IEEE values through locale-normalized `snprintf`.

`basic_json` construction routes through serializer hooks or active-type switches, then repairs diagnostic parent pointers and asserts storage invariants before returning.

## State And Persistence Behavior

There is no file, network, or database persistence in this chunk. State is in-memory and owned by the JSON object or serializer/writer instance:

- `iter_impl` stores a pointer to the owning JSON object plus one active internal iterator.
- `json_pointer` stores parsed tokens; it does not cache resolved nodes.
- output adapters store references to the destination vector/string/stream, so destination lifetimes must outlive serialization.
- `binary_writer` and `serializer` hold shared output adapters and reusable buffers.
- `basic_json::json_value` owns heap-allocated object/array/string/binary payloads through the configured allocator and stores primitive values directly.
- diagnostic builds add parent-pointer state and position metadata outside the normal JSON data model.

The main persistence-like behavior is deterministic serialization. The same JSON value should produce stable text and binary encodings subject to object ordering, selected format flags, locale normalization, and macro configuration.

## Dependencies And Integration Points

Internal dependencies include earlier sections of the same header:

- `value_t`, exception classes, macro configuration, `JSON_THROW`, `JSON_ASSERT`, and Hedley annotations;
- type-trait helpers such as `enable_if_t`, `is_usable_as_key_type`, `is_basic_json`, and `is_compatible_type`;
- `byte_container_with_subtype`, parser types, SAX types, binary reader declarations, and input format enums;
- string helpers `concat`, `escape`, and `unescape`;
- endian helper `little_endianness()`.

Standard library dependencies include algorithms, arrays, vectors, maps, strings, streams, allocators, numeric limits, locale metadata, `snprintf`, `memcpy`/`memmove`, type traits, and iterator traits.

External integration for XRootD is by inclusion. Consumers that use `XrdOucJson.hh` rely on this chunk for:

- `nlohmann::json` and `nlohmann::ordered_json` object behavior;
- pointer-based access such as `j.at(json::json_pointer("/path"))` or patch/flatten operations implemented later in the header;
- `dump()` and binary serialization APIs exposed later by `basic_json`;
- initializer-list syntax such as `json{{"key", value}}`;
- custom serializers and custom base classes.

Because this is a vendored third-party header, local changes have broad ABI/API consequences for every translation unit that includes it.

## Risks And Edge Cases

- Iterator comparisons are only defined for the same container. The implementation throws when `m_object` differs; callers that compare iterators from different JSON values will fail at runtime.
- Primitive JSON values expose a synthetic one-element iterator. Generic code that assumes only arrays/objects are iterable can accidentally process primitives.
- Object iterators do not support ordering, offsets, or `operator[]`; ordered/random-access algorithms must not be applied to object iterators.
- JSON Pointer array indexes reject leading zeroes and malformed numeric tokens. Inputs such as `/01`, `/a`, or `/-` are accepted or rejected differently depending on checked, unchecked, const, or append contexts.
- `get_unchecked()` mutates null nodes into arrays or objects based on token shape. This is convenient for `operator[]` but can surprise callers expecting read-only path probing.
- `flatten()` maps empty arrays/objects to `null`, so structural emptiness is not preserved through flatten/unflatten in the same way as non-empty containers.
- BSON requires a top-level object and rejects NUL bytes in keys. Large strings, arrays, or document sizes are cast into 32-bit BSON sizes, so extremely large inputs rely on upstream bounds and platform behavior.
- Binary writers have many format-specific integer size thresholds. Boundary mistakes around 23/24, 127/128, 255/256, 65535/65536, and signed minima would change wire encodings.
- `write_number()` depends on correct endian detection and on `CharType` byte-size/triviality assumptions. Signed `char` handling uses reinterpretation/memcpy to preserve byte values above 127.
- BJData ndarray handling trusts the three-key object schema, then directly reads numeric union members from `_ArraySize_` and `_ArrayData_`; malformed values can trigger assertions or invalid output if not rejected earlier.
- Text serialization emits non-finite floating-point values as `null`, which is valid JSON but loses NaN/Inf identity.
- Invalid UTF-8 behavior depends on the configured `error_handler_t`; strict mode throws, replace mode injects U+FFFD, and ignore mode can silently drop bytes.
- `ordered_map` lookup/insert/erase are linear and erase reconstructs elements manually because keys are const. Iterator invalidation follows vector semantics and can be more aggressive than map users expect.
- `basic_json::destroy()` intentionally avoids recursive destruction for nested arrays/objects. Bugs in this flattening destruction path can leak, double-destroy, or disturb diagnostic parent assumptions.
- Diagnostic parent pointers need repair after vector reallocation or ordered-map movement. The `set_parent` capacity checks and ordered-map branch are critical for useful exception diagnostics.
- Since this code is header-only and heavily macro-gated, behavior can change with `JSON_NO_IO`, `JSON_DIAGNOSTICS`, `JSON_HAS_CPP_14`, `JSON_HAS_THREE_WAY_COMPARISON`, `JSON_HAS_CPP_26`, and compiler-specific macros.

## Test Signals

Useful test coverage for this chunk should include:

- iterator begin/end, dereference, `key()`, `value()`, arithmetic, invalid object offsets, cross-container comparison errors, and primitive/null iteration;
- reverse iteration over arrays and objects, including object key/value access;
- JSON Pointer parse failures for missing leading slash and bad `~` escapes;
- pointer traversal for checked, unchecked, const, `contains`, append `"-"`, array-index overflow, leading-zero rejection, and null-to-container creation;
- `flatten()`/`unflatten()` round trips for nested objects/arrays, escaped keys containing `/` and `~`, empty arrays/objects, primitive leaves, and invalid flattened values;
- initializer-list construction distinguishing arrays from object-like two-element string-key arrays;
- text `dump()` for compact and pretty output, binary-as-object representation, `ensure_ascii`, invalid UTF-8 under all handlers, control characters, surrogate-pair output, integer minima, unsigned maxima, finite floats, NaN, and infinities;
- CBOR, MessagePack, UBJSON, BJData, and BSON golden-byte tests around every length and integer threshold;
- BSON top-level non-object rejection and NUL-key rejection;
- endian-sensitive binary numeric output on little- and big-endian targets or with explicit byte-order fixtures;
- `ordered_json` insertion order, duplicate-key behavior, lookup, erase, iterator invalidation expectations, and heterogeneous lookup where enabled;
- construction/destruction of very deeply nested arrays/objects to validate non-recursive destruction;
- diagnostic builds that assert parent links after insertion, erase, vector capacity growth, and ordered-map object mutation.

For XRootD integration, regressions are likely to appear as compile failures in translation units including `XrdOucJson.hh`, runtime JSON parse/dump mismatches, changed binary serialization bytes, or exception behavior changes in configuration paths that use JSON Pointer or object iteration.

### subset-b-007956: lines 21068-25716

# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucJson.hh lines 21068-25716

## Purpose

This chunk is the closing portion of XRootD's bundled nlohmann JSON 3.12.0 single-header implementation. It completes `basic_json`'s public API surface: explicit array/object/binary construction, copy/move lifetime handling, type inspection, conversion/access helpers, element access and mutation, lookup/iteration/capacity utilities, comparison, text and binary serialization/deserialization, JSON Pointer, JSON Patch, JSON Merge Patch, user-defined literals, `std` integrations, and final macro cleanup.

Within XRootD this header provides a self-contained JSON dependency under `src/XrdOuc`, so callers can parse, build, inspect, serialize, diff, patch, and convert JSON values without linking a separate JSON library. The code is generic upstream library code rather than XRootD-specific business logic, but it is an integration point for any XRootD component using `nlohmann::json` through this vendored header.

## Important APIs, Types, and Functions

- `basic_json::binary(...)` explicitly constructs `value_t::binary` values from a `binary_t::container_type`, optionally with a subtype. Both copy and move overloads are present.
- `basic_json::array(...)` and `basic_json::object(...)` force initializer-list construction into array or object mode.
- `basic_json(size_type cnt, const basic_json& val)` constructs an array with repeated values; `basic_json(InputIT first, InputIT last)` constructs a value from compatible JSON iterators and validates primitive iterator ranges.
- Copy/move constructors, assignment, and destructor manage `m_data`, diagnostic positions, parent pointers, and invariant checks.
- Type inspection APIs include `dump`, `type`, `is_primitive`, `is_structured`, `is_null`, `is_boolean`, number/string/object/array/binary/discarded checks, and implicit `operator value_t`.
- Value access APIs include `get`, `get_to`, `get_ref`, `get_ptr`, `get_binary`, implicit `operator ValueType`, and serializer-driven `JSONSerializer<ValueType>::from_json` dispatch.
- Element access APIs include `at(index)`, `at(key)`, `operator[](index)`, `operator[](key)`, JSON Pointer overloads, and `value(key_or_pointer, default)`.
- Mutation APIs include `erase`, `clear`, `push_back`, `operator+=`, `emplace_back`, `emplace`, `insert`, `update`, and `swap`.
- Lookup and iteration APIs include `find`, `count`, `contains`, `begin/end/cbegin/cend`, reverse iterators, `items`, and deprecated `iterator_wrapper`.
- Serialization/deserialization includes stream operators, `parse`, `accept`, `sax_parse`, `type_name`, binary writers/readers for CBOR, MessagePack, UBJSON, BJData, and BSON.
- JSON Pointer functions expose unchecked/checked pointer access, `flatten`, and `unflatten`.
- JSON Patch and Merge Patch APIs include `patch_inplace`, `patch`, static `diff`, and `merge_patch`.
- Nonmember support adds `nlohmann::to_string`, `_json` and `_json_pointer` literals, `std::hash<nlohmann::json>`, `std::less<value_t>`, and pre-C++20 `std::swap` specialization.

## Control Flow

Construction and assignment set `m_data.m_type` first, populate the matching `json_value` union arm, then call `set_parents()` and `assert_invariant()` where needed. Iterator-range construction rejects incompatible iterators, enforces full primitive ranges, copies primitive payloads directly, and creates new container storage for arrays/objects.

Access paths are strongly type-gated. `at()` performs type checks and range/key checks, throwing library exceptions with specific error IDs. Non-const `operator[]` has mutating semantics: null values are implicitly converted into arrays or objects, array access resizes with null fillers when the index is beyond the current size, and object access inserts `null` for missing keys. Const `operator[]` assumes the key/index is valid for the active type.

Conversion dispatch uses SFINAE priority tags. Pointer requests delegate to `get_ptr`; default-constructible target types use `JSONSerializer::from_json(json, out)`, non-default-constructible targets use a returning `from_json(json)`, JSON types copy `*this`, and reference access validates pointer compatibility.

Container mutation validates iterator ownership and target type before modifying storage. Array insertion centralizes through `insert_iterator`, which computes a stable offset before insertion and refreshes parent links afterwards. Object `update` can either overwrite keys or recursively merge object-valued keys when `merge_objects` is true.

JSON Patch applies operations sequentially to `*this` in `patch_inplace`. It first requires the patch document to be an array of objects, extracts typed members (`op`, `path`, `value`, `from`) through a local validator, maps operation strings to an enum, and executes add/remove/replace/move/copy/test. Add handles root replacement, object insertion, array append via `-`, and bounded array insertion. Remove finds object keys or erases array indices. Move copies the source value, removes it, then adds it at the target. Test compares with `operator==` and throws on mismatch. `patch` is the copy-on-write wrapper around `patch_inplace`.

`diff` recursively builds an RFC6902-style patch. Equal values produce an empty patch; type changes produce root/path replacement; arrays recurse over common indices, emit removals before additions for trailing source elements, and append trailing target elements at `/-`; objects recurse over shared keys, remove missing source keys, and add target-only keys.

`merge_patch` follows RFC7396-style behavior: object patches force the target to an object, null-valued members erase keys, non-null members recurse through `operator[]`, and non-object patches replace the target entirely.

## State and Persistence Behavior

Persistent state is the `data m_data` member, which contains `value_t m_type` and `json_value m_value`. The nested `data` destructor destroys the active union member according to `m_type`. Copy construction deep-copies heap-backed objects, arrays, strings, and binary values; move construction transfers `m_data` and nulls out the moved-from value. Assignment uses copy-and-swap semantics.

When `JSON_DIAGNOSTICS` is enabled, values track `m_parent`; resizing, insertion, swapping, copying, moving, and updates refresh parent links. When `JSON_DIAGNOSTIC_POSITIONS` is enabled, parse position fields are copied/moved/swapped and exposed via `start_pos()` and `end_pos()`.

The code does not persist data to disk by itself. Persistence-facing behavior is serialization through `dump`, stream `operator<<`, binary `to_*` functions, and parsing/deserialization through `parse`, stream `operator>>`, `from_*`, and SAX APIs. Failed binary parses return `value_t::discarded` when exceptions are disabled; text parse behavior depends on `allow_exceptions`.

## Dependencies and Integration Points

This code depends on the earlier portions of the same header for `value_t`, `json_value`, allocators, `binary_t`, `serializer`, `parser`, `binary_writer`, `binary_reader`, `json_pointer`, iterator types, `iteration_proxy`, diagnostics helpers, exception classes, SFINAE traits, `input_adapter`, and `output_adapter`.

It integrates with the C++ standard library via containers, iterators, allocators, streams, `std::hash`, `std::less`, `std::swap`, type traits, partial ordering when C++20 comparison is available, and optional `char8_t` literal overloads. It is controlled by compile-time macros such as `JSON_NO_IO`, `JSON_HAS_CPP_14/17/20`, `JSON_HAS_THREE_WAY_COMPARISON`, `JSON_DIAGNOSTICS`, `JSON_DIAGNOSTIC_POSITIONS`, `JSON_USE_GLOBAL_UDLS`, and `JSON_TEST_KEEP_MACROS`.

For XRootD code, practical integration points are any component that includes `XrdOucJson.hh` and uses `nlohmann::json` for configuration, protocol payloads, logging payloads, or structured metadata. The final macro cleanup also matters to integration: most JSON/Hedley macros are undefined at the end of the header to avoid leaking into XRootD translation units.

## Risks and Edge Cases

- `operator[]` is intentionally mutating for null/object/array values; callers that only intend lookup should prefer `at`, `find`, `contains`, or `value` to avoid implicit object/array creation or array expansion.
- Const object `operator[]` asserts key existence rather than returning a default; using it for unchecked lookup can fail under assertions or become undefined if assumptions are wrong.
- `get_ptr`, `get_ref`, and `get_binary` expose or return references to internal storage. Pointers/references become invalid after mutations that reallocate or change the active value.
- Numeric comparison casts mixed signed/unsigned values through `number_integer_t` in some cases, which is upstream behavior but can be surprising around large unsigned values. Floating NaN and discarded values are treated as unordered.
- JSON Patch is not transactional in `patch_inplace`; operations before a later failing operation remain applied. `patch` should be used when callers need the original value preserved on failure.
- `patch_inplace` assumes each patch element is an object before `get_value` uses `val.m_data.m_value.object`; the explicit object check protects that path, but refactoring order would be risky.
- Binary parse APIs return `discarded` on failure when configured not to throw, so callers must check `is_discarded()` before using the result.
- Stream operators and deprecated overloads are gated by `JSON_NO_IO`; builds disabling I/O lose those integration points.
- Macro cleanup is broad. Translation units relying on JSON macros after including this header must opt into `JSON_TEST_KEEP_MACROS` or include/order code carefully.

## Test Signals

Useful coverage for XRootD's vendored copy should include compile-only tests across the supported compiler modes and macro configurations used by the project, especially with and without `JSON_NO_IO`, diagnostics, and C++20 comparisons. Behavioral tests should exercise parsing/dumping round trips, `at` versus `operator[]` behavior, defaulted `value` lookups, iterator-range construction and invalid iterator errors, object updates with and without recursive merging, JSON Pointer flatten/unflatten, all JSON Patch operations including failure cases, Merge Patch key deletion/replacement, and binary format round trips for CBOR/MessagePack/UBJSON/BJData/BSON.

Regression signals include exception IDs/messages for type/range errors, preservation of parent diagnostics after resize/insert/swap/update, `discarded` results when binary parse failures are non-throwing, NaN/discarded comparison behavior, literal parsing for `_json` and `_json_pointer`, and successful inclusion of the header without leaking macros into downstream XRootD code.
