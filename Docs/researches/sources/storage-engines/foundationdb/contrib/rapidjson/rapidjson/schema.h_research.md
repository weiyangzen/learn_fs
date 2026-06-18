# sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/schema.h

## Purpose

`schema.h` implements RapidJSON's JSON Schema support. It compiles a JSON schema document into immutable internal schema nodes and validates JSON SAX event streams against type, structural, string, numeric, combinator, reference, and dependency constraints.

## Important APIs and Types

The main public types are `GenericSchemaDocument<ValueT, Allocator>`, `SchemaDocument`, `GenericSchemaValidator<SchemaDocumentType, OutputHandler, StateAllocator>`, `SchemaValidator`, `IGenericRemoteSchemaDocumentProvider`, and `SchemaValidatingReader`. Internally, `internal::Schema` represents one compiled schema node, `SchemaValidationContext` stores per-node validation state, `Hasher` computes order-sensitive array and order-insensitive object hashes for `enum` and `uniqueItems`, and `ISchemaStateFactory` lets schemas create nested validators, hashers, and state allocations.

## Control Flow

`GenericSchemaDocument` recursively walks the source schema, creates `internal::Schema` nodes keyed by JSON Pointer, and resolves `$ref` entries. Local references are deferred in `schemaRef_` until the initial graph is built; remote references are resolved immediately through an optional `IRemoteSchemaDocumentProvider`. Each `Schema` constructor inspects recognized keywords and prepares type bitmasks, enum hashes, all/any/one/not validator slots, properties, pattern properties, required flags, dependencies, additional property/item rules, tuple/list item schemas, string length/pattern rules, and numeric bounds.

`GenericSchemaValidator` is itself a SAX handler. For each incoming value it pushes the applicable schema context, calls the current schema's keyword-specific method, forwards events to parallel validators for `allOf`, `anyOf`, `oneOf`, `not`, schema dependencies, and pattern properties, then passes valid events to the output handler. Object keys append JSON Pointer tokens, select property/pattern/additional-property schemas, and track required/dependency existence. Array values select list, tuple, or additional item schemas and append numeric pointer tokens. `EndValue` checks enum/combinator/not outcomes, updates `uniqueItems` hashes in the parent array, pops schema context, and trims the document pointer stack.

## State and Persistence

`GenericSchemaDocument` owns compiled schema nodes in `schemaMap_`, unresolved reference records in `schemaRef_`, and an allocator if one was not supplied. It is immutable after construction. `GenericSchemaValidator` stores mutable validation state in `schemaStack_`, document pointer text in `documentStack_`, a `valid_` flag, optional allocator ownership, and nested validator/hash state allocated through the state factory. No state is persisted outside memory.

## Dependencies and Integration Points

The header depends on `document.h`, `pointer.h`, numeric math, RapidJSON allocators/stacks, and either RapidJSON's internal regex engine, `std::regex`, or no regex depending on compile-time macros. It integrates directly with `reader.h` through SAX handler methods and with downstream handlers through validator event forwarding. Verbose mode optionally uses `stringbuffer.h` for diagnostic pointer output.

## Risks and Edge Cases

Regex support is compile-time dependent; invalid patterns become null and therefore silently disable matching for that pattern. Property lookup is linear over gathered property names, which can be costly for very large object schemas. `multipleOf` for doubles checks an exact floating remainder and can be sensitive to representation error. `uniqueItems` uses hash codes, so correctness depends on hash collision improbability rather than structural comparison. `$ref` handling supports JSON Pointer fragments and provider-backed remote documents, but unresolved or invalid references degrade to typeless behavior through default schema pointers. The implementation targets an older JSON Schema dialect and ignores unknown keywords.

## Test Signals

Tests should validate every supported keyword family: type, enum, allOf/anyOf/oneOf/not, object properties, required, property and schema dependencies, patternProperties, additionalProperties, min/maxProperties, list and tuple items, additionalItems, uniqueItems, min/maxItems, min/maxLength with multibyte code points, pattern matching with available regex backend, minimum/maximum exclusivity, integer/number distinctions, multipleOf, local and remote `$ref`, invalid-schema tolerance, invalid schema/document pointer reporting, validator reset/reuse, and `SchemaValidatingReader` parse-error plus schema-error combinations.
