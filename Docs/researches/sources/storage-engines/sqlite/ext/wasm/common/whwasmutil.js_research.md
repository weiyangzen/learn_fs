# sources/storage-engines/sqlite/ext/wasm/common/whwasmutil.js

## Purpose

`whwasmutil.js` installs a browser-oriented utility layer for arbitrary WebAssembly modules, with SQLite WASM as a primary consumer. It intentionally overlaps with useful parts of Emscripten glue while staying usable outside Emscripten-generated environments. The installer attaches memory, pointer, string, allocation-scope, indirect-function-table, and C export wrapper helpers to a caller-supplied target object.

The file also exposes `WhWasmUtilInstaller.yawl()`, a small loader factory for instantiating a WASM module and optionally installing these utilities onto a target.

## Important APIs, Types, and Functions

- `globalThis.WhWasmUtilInstaller(target)`: main installer. It configures pointer representation, heap views, string helpers, function table helpers, allocation scopes, and export wrappers.
- `target.ptr`: read-only pointer helper object with `size`, `ir`, `null`, `coerce()`, `add()`, and `addn()`. It hides whether pointers are JS `Number` or `BigInt`.
- Heap accessors: `heap8()`, `heap8u()`, `heap16()`, `heap16u()`, `heap32()`, `heap32u()`, and `heapForSize()`. They refresh typed-array views after memory growth.
- Function table helpers: `functionTable()`, `functionEntry()`, `jsFuncToWasm()`, `installFunction()`, `scopedInstallFunction()`, and `uninstallFunction()`.
- Memory value helpers: `peek()`, `poke()`, pointer variants, numeric width variants, and deprecated Emscripten-style aliases.
- String helpers: `cstrlen()`, `cstrToJs()`, `jstrlen()`, `jstrcpy()`, `cstrncpy()`, `jstrToUintArray()`, `allocCString()`, and `scopedAllocCString()`.
- Scoped allocation helpers: `scopedAllocPush()`, `scopedAllocPop()`, `scopedAlloc()`, `scopedAllocCall()`, `allocPtr()`, `scopedAllocPtr()`, `allocMainArgv()`, `scopedAllocMainArgv()`, and `cArgvToJs()`.
- Export wrappers: `xGet()`, `xCall()`, `xWrap()`, `xCallWrapped()`, `xWrap.argAdapter()`, `xWrap.resultAdapter()`, and `xWrap.FuncPtrAdapter`.
- `WhWasmUtilInstaller.yawl(config)`: WASM loader using `WebAssembly.instantiateStreaming()` when available and falling back to `arrayBuffer()` instantiation.

## Control Flow

Installer startup first derives `bigIntEnabled`, pointer size, and pointer IR from explicit config or, if allocation is already available, a probe allocation. It replaces `pointerSize` and `pointerIR` with the read-only `target.ptr` facade. It then installs a lazy `exports` getter if `target.exports` is not already present, creates the internal `cache`, and registers heap, function-table, memory, string, allocation, and wrapper helpers on `target`.

Heap access flows through `heapWrappers()`, which caches typed-array views over `WebAssembly.Memory.buffer` and rebuilds them when the buffer grows. Function installation uses the indirect function table, preferring reuse of indexes from `cache.freeFuncIndexes`, growing the table when needed, and compiling plain JS functions into tiny one-function WASM modules through `jsFuncToWasm()`.

`xWrap()` is the higher-level binding path. It resolves a WASM export, JS function, or indirect function pointer, validates arity and adapters, pushes a scoped allocation frame, converts arguments, calls the underlying function, converts the result, and finally pops the allocation frame so transient C strings and scoped function pointers are cleaned up.

`yawl()` returns a loader function. On load completion it installs `module`, `instance`, memory, and optional malloc/free wrappers onto `config.wasmUtilTarget`, runs `WhWasmUtilInstaller()` on that target, calls `config.onload`, and resolves with the load result plus `config`.

## State and Persistence

All runtime state is held in the closure-local `cache`: heap typed arrays, heap size, `WebAssembly.Memory`, reusable function table indexes, scoped allocation stacks, UTF-8 encoder/decoder, and `xWrap` adapter maps. It does not persist browser storage or files. It does manage WASM heap and indirect-function-table lifetime, so cleanup correctness depends on clients matching `alloc` with `dealloc`, `installFunction` with `uninstallFunction`, and `scopedAllocPush` with `scopedAllocPop`.

## Dependencies and Integration Points

The code depends on browser-level `TextEncoder`, `TextDecoder`, `WebAssembly.Memory`, `WebAssembly.Table`, `WebAssembly.Module`, `WebAssembly.Instance`, `fetch`, and optionally `BigInt64Array`/`BigUint64Array`. The target object must expose `exports` or `instance.exports`, and most allocation APIs require `alloc()` and `dealloc()` with malloc/free semantics. SQLite integrates this layer as `sqlite3.wasm`, using `xWrap()` for C API bindings, `allocMainArgv()` for shell-like `main()` calls, and `FuncPtrAdapter` for callback-function pointer bindings.

## Risks and Edge Cases

- BigInt handling must match the compiled WASM module. Enabling BigInt in JS is not enough if the module lacks 64-bit integration.
- `peek()` and `poke()` coerce BigInt pointers to `Number` for typed-array indexing, so impossible or out-of-browser-range addresses can misbehave.
- `cstrncpy()` has a likely typo in the negative-length path: it refers to `strPtr` instead of `srcPtr`.
- Function table growth can fail if the table is not growable, for example in Emscripten builds without table growth.
- `scopedAllocPop()` decides whether a scoped pointer is a function pointer by checking `functionEntry(p)`. A heap pointer value colliding with a live function table index would be ambiguous, though typical address spaces make that unlikely.
- `xWrap()` is intentionally strict about arity. This catches binding mistakes but can reject exotic JS functions whose `length` does not reflect intended callable arity.

## Test Signals

Useful tests should cover 32-bit and 64-bit pointer modes, heap growth invalidating cached views, UTF-8 round trips including multibyte and empty strings, allocation-scope cleanup on exceptions, table slot reuse after `uninstallFunction()`, `FuncPtrAdapter` modes, and `xWrap()` conversions for string, JSON, pointer, numeric, and deallocating result adapters. SQLite's worker and fiddle demos exercise many of these paths indirectly through `xWrap()`, shell startup, callback handling, and database export/import.
