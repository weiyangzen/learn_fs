# sources/storage-engines/sqlite/ext/wasm/api/sqlite3-worker1.c-pp.js

## Purpose
This is the worker entrypoint for SQLite Worker API #1. It loads the generated sqlite3 JavaScript module, initializes it, then starts the worker API by calling `sqlite3.initWorker1API()`. The indirection is necessary because a worker that directly loads `sqlite3.js` cannot reliably call `sqlite3InitModule()` in the right order or visibility context.

## Important APIs, Types, and Functions
The file imports or loads `sqlite3InitModule` using build-mode-specific code. Bundler-friendly ES module builds import `./sqlite3-bundler-friendly.mjs`; ES module builds import `./sqlite3.mjs`; classic builds use `importScripts()` to load `sqlite3.js`. After loading, it calls `sqlite3InitModule().then(sqlite3 => sqlite3.initWorker1API())`.

The worker API started by `initWorker1API()` is expected to post the ready message `{type:'sqlite3-api', result:'worker1-ready'}`, which is consumed by clients such as `sqlite3-worker1-promiser.c-pp.js`.

## Control Flow
In classic builds, the file inspects `globalThis.location.href` search parameters. If `sqlite3.dir` exists, it prepends that directory when building the `sqlite3.js` URL; otherwise it loads `sqlite3.js` from the current worker script location. Once the script or module import has provided `sqlite3InitModule`, initialization is asynchronous and the Worker API is installed only after the sqlite3 module Promise resolves.

If the build is compiled with `omit-oo1`, the file is replaced by a comment because Worker API #1 depends on the OO1 layer.

## State and Persistence Behavior
This file owns no persistent state. It controls module-loading state in the worker global scope and delegates all database, VFS, and message handling state to the initialized sqlite3 module and Worker API #1 implementation.

## Dependencies and Integration Points
Dependencies are Web Worker globals, `importScripts()` for classic builds, ES module imports for module builds, `sqlite3InitModule`, and `sqlite3.initWorker1API()`. It integrates directly with worker clients that wait for the ready message, especially the promiser wrapper. The `sqlite3.dir` URL argument is a path integration point for deployments that host generated sqlite3 assets outside the worker entrypoint directory.

## Risks and Edge Cases
Wrong asset paths will fail before the ready message is posted, leaving clients waiting or receiving worker errors. Module type must match the artifact: module workers need the `.mjs` variants, while classic workers need `importScripts`. The file assumes `sqlite3InitModule()` resolves successfully; initialization failures are not caught here. Builds without OO1 cannot use this worker entrypoint.

## Test Signals
Tests should instantiate the worker in classic, ES module, and bundler-friendly build modes where applicable, verify the ready message is posted after initialization, verify `sqlite3.dir` path rewriting, and perform a simple open/exec/close through Worker API #1 or the promiser wrapper. Negative tests should cover missing asset paths and omit-OO1 builds.
