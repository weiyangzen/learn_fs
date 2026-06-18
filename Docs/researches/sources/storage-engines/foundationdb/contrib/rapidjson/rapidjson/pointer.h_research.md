# sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/pointer.h

Purpose: This header implements RFC 6901 JSON Pointer support for RapidJSON DOM values, including parsing, stringification, querying, creation, mutation, defaulting, swapping, erasing, and convenience free functions.

Important APIs and types: Public types include `PointerParseErrorCode`, `GenericPointer<ValueType, Allocator>`, nested `Token`, typedef `Pointer`, and helpers such as `CreateValueByPointer`, `GetValueByPointer`, `GetValueByPointerWithDefault`, `SetValueByPointer`, `SwapValueByPointer`, and `EraseValueByPointer`. `Token` stores name, code-unit length, and parsed array index or `kPointerInvalidIndex`.

Control flow: Parsing detects plain or URI-fragment form, splits on `/`, unescapes `~0` and `~1`, percent-decodes URI fragments, validates required percent encoding, and detects numeric array indexes without leading zeros or overflow. `Get()` walks objects by member name and arrays by numeric index. `Create()` walks or builds the path, converting parents to object or array as implied by tokens, growing arrays with nulls, and treating `"-"` as append. `Set`, `GetWithDefault`, and `Swap` are layered on `Create`; `Erase` walks to the parent and removes a member or array element.

State and persistence behavior: A parsed pointer owns an allocator optionally, one contiguous allocation for tokens plus name buffer, parse error offset/code, and token count. User-supplied token construction avoids allocation and leaves token lifetime external. DOM mutation persists in the caller's `GenericValue`/`GenericDocument`, not in the pointer.

Dependencies and integration points: It includes `document.h` and `internal/itoa.h`, and uses encodings/transcoders for URI fragments. It is a high-level DOM integration point.

Risks: `Create()` can change parent types and discard existing values when the path implies a different shape. URI fragment handling is strict about percent encoding. Equality returns false for invalid pointers regardless of token equality. User-supplied tokens must outlive the pointer. Array growth can allocate large null-filled arrays for large indexes.

Test signals: Cover RFC examples, empty pointer root access, invalid escapes and percent encodings, URI fragment stringification, numeric index detection and overflow, leading-zero object keys, `"-"` append, `Create()` type conversion, `Get()` unresolved-token index, default insertion, erase root failure, object/array erasure, copy/assignment ownership, and helper free functions.
