# sources/storage-engines/sqlite/ext/wasm/jaccwabyt/jaccwabyt.js

## Purpose

`jaccwabyt.js` exposes `globalThis.Jaccwabyt`, a struct-binding factory for WASM memory. Given allocation functions, heap access, pointer settings, and struct descriptions, it generates JS constructor classes whose properties read and write native C struct fields through `DataView`.

SQLite uses this to bind C structs in its WASM layer, especially where JS needs structured access to memory layouts produced by C.

## Important APIs, Types, and Functions

- `StructBinderFactory(config)`: top-level factory. Validates `heap`, `alloc`, `dealloc`, optional `realloc`, pointer config, BigInt availability, and debug settings.
- Signature helpers: `isFuncSig()`, `isPtrSig()`, `sigLetter()`, `sigIR()`, `sigSize()`, `sigDVGetter()`, `sigDVSetter()`, and `sigDVSetWrapper()`.
- Instance handle storage: `getInstanceHandle()` uses a `WeakMap` to associate JS struct wrappers with pointer metadata.
- Lifetime helpers: `__allocStruct()`, `__freeStruct()`, `__addOnDispose()`, `__allocCString()`, and `__setMemberCString()`.
- `StructType`: base prototype for all generated struct wrappers. It provides `dispose()`, `lookupMember()`, `memberToJsString()`, `memberIsString()`, `memberKey()`, `memberKeys()`, `memberSignature()`, `memoryDump()`, `extraBytes`, `zeroOnDispose`, `pointer`, `setMemberCString()`, and `addOnDispose()`.
- Adapters: `StructBinder.adaptGet()`, `adaptSet()`, and `adaptStruct()` register reusable member/struct conversion proxies.
- `makeMemberStructWrapper()` and `makeMemberWrapper()`: generate property accessors for nested structs and scalar/pointer fields.
- `StructBinderImpl()` / `StructBinder()`: produce concrete struct constructors from struct descriptions.

## Control Flow

Factory initialization normalizes `config.heap` into a function returning a `Uint8Array`, validates allocation callbacks, determines pointer size and representation, sets up debug flags, and defines helper functions. Calling `StructBinder(name, structInfo)` creates a concrete constructor. The struct description is normalized, optional adapters are installed, offsets and sizes are validated or auto-calculated, and one accessor is generated per member.

Constructing a generated struct either wraps an external pointer or allocates new heap memory, optionally with extra bytes, ownership transfer, zero-on-dispose, and on-dispose callbacks. Reading a member creates a `DataView` over the current heap buffer at `this.pointer + offset`, calls the signature-specific getter, and applies optional getter proxies. Writing validates pointer/null/struct values as needed, applies optional setter proxies, coerces to `Number` or `BigInt`, and calls the signature-specific setter. Disposing runs on-dispose callbacks, clears optional memory, frees owned memory, and removes the weak-map handle.

Nested structs are represented by generated child constructors. Accessing a nested member returns a wrapper over the parent memory at the nested offset, caches it by parent pointer and member key, and arranges cleanup when the parent or child is disposed.

## State and Persistence

State is in closure-local config, debug flag objects, adapter weak maps, the instance handle `WeakMap`, and nested-struct caches. Native state lives in WASM heap memory allocated by `config.alloc` or externally supplied pointers. The library has no browser persistence. Memory ownership is explicit: generated instances either own allocated memory and free it on `dispose()`, or wrap external memory and leave freeing to the external owner unless ownership is transferred.

## Dependencies and Integration Points

The factory requires a WASM heap as `WebAssembly.Memory` or a heap-returning function, `alloc()` and `dealloc()`, and optionally `realloc()`, `log`, pointer size/IR, and BigInt support. It depends on `DataView`, `TextEncoder`, `TextDecoder`, `WeakMap`, `Map`, and optionally `BigInt64Array`. It is designed to pair with `whwasmutil`-style allocation and pointer helpers but can run with any compatible WASM environment.

## Risks and Edge Cases

- Struct descriptions must match the C ABI exactly unless `autoCalcSizeOffset` is being used for pure-JS/test structures. Incorrect offsets or sizes cause silent memory corruption or wrong reads before validation can catch all cases.
- `autoCalcSizeOffset` is explicitly dangerous for real C structs because JS cannot infer compiler padding and alignment.
- Pointer-size and BigInt configuration must match the compiled module.
- Property access after `dispose()` can fail or read invalid memory depending on the member path; setters explicitly reject disposed objects.
- On-dispose callbacks intentionally do not propagate exceptions, so cleanup failures are warnings rather than thrown failures.
- Nested struct caching keys combine pointer and property name. Reuse of native addresses after disposal can make cleanup discipline important.
- Signature/adaptor names are checked to avoid collisions with data type signatures, but misuse of custom adapters can still corrupt values.

## Test Signals

Tests should create generated structs with explicit offsets and with auto-calculated test layouts, read/write all scalar signatures, exercise 32-bit and 64-bit pointer modes, verify string allocation and `setMemberCString()` disposal, validate nested struct wrappers and cleanup, wrap external pointers with and without ownership transfer, test `extraBytes` and `zeroOnDispose`, confirm read-only setters throw, confirm invalid signatures and unaligned sizes throw, and verify debug flags do not alter behavior.
