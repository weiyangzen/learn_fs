# sources/storage-engines/sqlite/ext/wasm/api/sqlite3-worker1-promiser.c-pp.js

## Purpose
This file implements a Promise-based client wrapper for SQLite Worker API #1. It can run in the main thread or in a worker that supports nested workers, creates or accepts a worker loading `sqlite3-worker1.js`, and turns request/response message exchanges into Promises. It is omitted when OO1 is omitted because Worker API #1 depends on the higher-level API.

## Important APIs, Types, and Functions
The main global is `sqlite3Worker1Promiser(config)`, which returns a stateful `promiserFunc`. Calls may be `promiserFunc(type, args)` or `promiserFunc({type, args, ...})`. The config accepts `worker`, `onready`, `onunhandled`, `generateMessageId`, `debug`, and an internal `onerror`. The default config creates a worker from the appropriate build artifact: bundler-friendly module, ES module, or classic `sqlite3-worker1.js`, preserving `sqlite3.dir` URL handling where relevant.

`sqlite3Worker1Promiser.v2(config)` wraps the original API and returns a Promise that resolves to the promiser function after the worker emits the ready message. In ES module builds, v2 is exported as default and the temporary global is deleted.

## Control Flow
The factory normalizes config, instantiates a worker if `worker` is a function, replaces `worker.onmessage`, and maintains `handlerMap` keyed by generated message IDs. The ready event is identified as `{type:'sqlite3-api', result:'worker1-ready'}` and triggers `onready(promiserFunc)`. Normal response messages look up `handlerMap[messageId]`, delete it, reject on `type:'error'`, update current `dbId` on open/close, and resolve with the worker payload.

When sending, the promiser builds or accepts a message envelope, injects the current `dbId` for non-open messages unless one is already set, assigns a unique `messageId`, records `departureTime`, stores resolve/reject handlers, and posts to the worker. For `exec` with a function callback, it synthesizes a row callback ID (`messageId + ':row'`), replaces `args.callback` with that string for the worker protocol, and routes per-row worker messages by temporary `handlerMap` entry. String callbacks are rejected because the promiser owns `worker.onmessage` and cannot dispatch arbitrary client message types.

## State and Persistence Behavior
State is entirely in JavaScript: `handlerMap`, optional generated message ID counters, and the current `dbId` used as the default target database. No database state is persisted by this wrapper; persistence is handled by the worker and SQLite. The row callback handler is removed in `finally()` so it is cleared after the exec request settles.

## Dependencies and Integration Points
The file depends on Web Workers, `performance.now()`, `URL`, `import.meta.url` in module builds, `document.currentScript` in classic builds, and the Worker API #1 message protocol implemented by `sqlite3.initWorker1API()`. It integrates with `sqlite3-worker1.c-pp.js`, which posts the ready message after module initialization. The default worker path logic keeps classic and module builds aligned with generated artifact names.

## Risks and Edge Cases
The factory replaces `worker.onmessage`, so callers cannot independently use `onmessage` on the same worker without going through `onunhandled`. Message IDs must be unique; custom generators that collide will misroute or leak Promises. `dbId` defaulting is convenient for a single active DB but can surprise multi-DB clients unless they pass explicit `dbId`. Per-row callbacks arrive asynchronously as worker messages and must tolerate the final row message with `row=undefined` and `rowNumber=null`. v1 readiness uses a callback rather than a Promise, so v2 is safer for module-style initialization.

## Test Signals
Tests should cover default worker creation paths for classic/module builds, ready callback and v2 Promise resolution, open setting `dbId`, close clearing it, error messages rejecting, unhandled messages reaching `onunhandled` or `onerror`, custom message ID generation, exec function callbacks receiving row and end-of-result messages, string exec callbacks throwing, and cleanup of row handlers after success or failure.
