# Research: sources/user-network-fs/rclone/fs/rc/js/loader.js

## sources/user-network-fs/rclone/fs/rc/js/loader.js

Purpose: browser loader/demo for the rclone rc WebAssembly build. It dynamically loads `wasm_exec.js`, instantiates `rclone.wasm`, runs the Go runtime, waits for `rcValid`, and logs sample rc calls.

Control flow creates a global `rcValid` promise and resolver, injects a script tag, polyfills `WebAssembly.instantiateStreaming` when missing, constructs `new Go()`, fetches and instantiates wasm, and runs the module. After validity resolves, it calls `rc("core/version")`, `rc/noop`, `operations/mkdir`, and `operations/list` against a memory remote. State is global browser variables `rc`, `rcValidResolve`, and `rcValid`, plus DOM script insertion and the WebAssembly runtime. Dependencies include Go’s `wasm_exec.js`, `rclone.wasm`, browser fetch/WebAssembly APIs, and a wasm-exported `rc` function. Risks include globals, no fetch/instantiate error handling, sample calls running automatically, and dependency on same-origin assets. No automated tests are present.
