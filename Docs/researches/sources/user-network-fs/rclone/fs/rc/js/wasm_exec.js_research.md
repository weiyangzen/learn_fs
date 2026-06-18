# sources/user-network-fs/rclone/fs/rc/js/wasm_exec.js

## Purpose
This is the Go WebAssembly JavaScript support runtime, adapted from the Go project. It defines `globalThis.Go`, polyfills minimum Node/browser-like `fs` and `process` behavior when absent, and implements the import functions required by Go's `runtime` and `syscall/js` packages.

## Important APIs, Types, and Functions
- `globalThis.Go` class encapsulates argv/env setup, WebAssembly import object construction, JS value reference tables, timeout scheduling, and program execution.
- `run(instance)` validates the `WebAssembly.Instance`, initializes memory/value tables, writes argv/env strings into linear memory, calls the Go `run` export, and waits for program exit.
- `_resume` and `_makeFuncWrapper` support Go callbacks invoked from JavaScript.
- Import handlers cover runtime time functions, random data, writes, JS property access, calls, construction, `instanceof`, and byte copies between Go and JS.

## Control Flow
The IIFE first installs minimal `fs` and `process` shims if needed, then validates required browser primitives (`crypto`, `performance`, `TextEncoder`, `TextDecoder`). The constructor builds `importObject.go` with many functions that interpret the Go stack pointer and read/write WASM memory. Runtime events use `_scheduledTimeouts` and `_pendingEvent` to resume Go from JS callbacks.

## State and Persistence
State is entirely in-memory: `_values`, `_goRefCounts`, `_ids`, `_idPool`, timeout maps, instance references, and the buffered stdout line accumulator. There is no filesystem persistence beyond writes delegated to an existing or shimmed `fs`.

## Dependencies and Integration Points
The file is required by Go-compiled WASM modules using `syscall/js`. `main.go` depends on this runtime to expose JavaScript globals and function callbacks. Host pages must instantiate WASM with `go.importObject` and call `go.run(instance)`.

## Risks and Edge Cases
The fallback `fs` implementation only supports writes and returns ENOSYS for most operations, so Go code doing real filesystem calls will fail. Reference counting bugs or failing to finalize Go refs can leak JS values. The runtime assumes layout contracts with the Go compiler/linker; version mismatch with a differently generated `.wasm` can break imports. Host environments must provide secure `crypto.getRandomValues`.

## Test Signals
There are no repository-local tests for this vendored/runtime file. Compatibility should be validated by running the browser WASM build under the same Go toolchain version that provided this file.
