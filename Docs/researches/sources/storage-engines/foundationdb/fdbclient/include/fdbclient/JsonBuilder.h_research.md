# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/JsonBuilder.h

## Purpose
Implements an append-only JSON string builder optimized for linear status construction without building a full mutable JSON tree. It supports null, object, and array outputs, typed value serialization, nested builder splicing, and a setter syntax for object keys.

## Important APIs, Types, And Functions
`JsonBuilder` tracks type, arena-backed text chunks, element count, and byte count. `getJson()` finalizes the document by appending the implicit closing suffix returned by `getEnd()`. `writeValue()` overloads handle `json_spirit::mValue`, booleans, integers, doubles, strings, `StringRef`, C strings, and nested `JsonBuilder` instances. `writeCoercedAsciiNumber()` emits numeric strings after validation. `JsonBuilderArray::push_back()` appends values, and `addContents()` copies from `json_spirit::mArray` or another builder. `JsonBuilderObject::setKey()`, `setKeyRawNumber()`, `operator[]`, and `addContents()` write key/value pairs. `JsonBuilderObjectSetter` backs assignment syntax.

## Control Flow
Builders start as null until object/array subclasses write the opening delimiter. Each appended array element or object key increments `elements` and emits a comma after the first item. Nested builders transfer chunk references and arena dependencies, then append their implicit terminator. Finalization is lazy: object and array closing delimiters are not stored until `getJson()` or nested writing asks for `getEnd()`.

## State And Persistence Behavior
State is entirely in-memory and arena-backed. `getJson()` returns an owned `std::string`; until then, content lives in `jsonText` chunks. `_addContents()` and nested builder writes share arena dependencies and mutate the source builder's chunk list to avoid unsafe shared tail capacity.

## Dependencies And Integration Points
The header depends on Flow arenas, tracing format helpers, JSONDoc/json_spirit value types, and C formatting. It integrates with client status, idempotency status, schema/status generation, and any code needing low-overhead JSON emission.

## Risks And Test Signals
Risks include incomplete string escaping for non-ASCII/control characters beyond the explicit escape set, duplicate object keys, raw key names not being escaped, finite/non-finite double coercion policy surprises, and builder sharing after splicing. Test signals should include valid JSON parsing of generated output, nested builder composition, raw-number coercion failures, escaping cases, duplicate key handling expectations, and byte/final-length accounting.
