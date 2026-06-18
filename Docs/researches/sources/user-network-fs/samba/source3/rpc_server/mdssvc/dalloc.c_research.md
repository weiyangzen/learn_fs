# sources/user-network-fs/samba/source3/rpc_server/mdssvc/dalloc.c

## Purpose
This file implements `DALLOC_CTX`, a small talloc-backed dynamic object store used by mdssvc Spotlight marshalling code to represent heterogeneous arrays, dictionaries, file metadata, and primitive values with runtime type tags. It gives the marshaller a compact way to build nested typed trees without defining a full variant object model.

## Important APIs, Types, And Functions
`struct dalloc_ctx` contains one `void **dd_talloc_array` vector whose elements are talloc children or copied talloc chunks named with their logical type. `_dalloc_new()` allocates a named context. `_dalloc_add_talloc_chunk()` appends either a copied scalar chunk (`size != 0`) or a type-checked talloc child (`size == 0`). `dalloc_size()`, `dalloc_get_object()`, and `dalloc_get_name()` expose vector inspection. `dalloc_get()` walks optional nested `DALLOC_CTX` entries and returns a type-checked element by index. `dalloc_value_for_key()` treats a context as alternating `"char *"` keys and values. `dalloc_stradd()` stores strings with the canonical `"char *"` name. `dalloc_dump()` recursively renders a debug representation of supported mdssvc types.

## Control Flow
Appending grows the array with `talloc_realloc()`, then either copies data into a named talloc chunk or validates that the supplied object has the requested talloc name. Retrieval functions parse varargs paths, stepping into nested `DALLOC_CTX` elements until the final type and index/key are reached. Dumping iterates every object, dispatches on the talloc type name, recurses for nested dalloc-compatible containers, formats scalar values, converts UTF-16LE strings to UTF-8 for logging, and expands CNID arrays recursively.

## State And Persistence
All state is in-memory and owned by the parent talloc context. There is no file or database persistence. Object identity and type safety depend on talloc names, so type names are part of the runtime state. `dalloc_dump()` allocates its returned string under the dumped object.

## Dependencies And Integration Points
The implementation depends on talloc, Samba charset conversion helpers, `talloc_stack`, time formatting, and mdssvc marshalling type definitions from `marshalling.h`. It is consumed by `marshalling.c` for Spotlight RPC pack/unpack trees and by parser/mdssvc code that builds or inspects metadata dictionaries.

## Risks And Test Signals
Risks include varargs misuse with no compile-time checking, negative indexes not rejected before comparison with `size_t` lengths, reliance on exact talloc names for type safety, dictionary lookups assuming alternating string key/value layout, and `localtime()` use in dumps. Test signals should cover scalar copy/add, nested array traversal, dictionary key lookup, type mismatch failure, out-of-range paths, UTF-16 dump conversion, CNID dump recursion, and talloc lifetime cleanup.
