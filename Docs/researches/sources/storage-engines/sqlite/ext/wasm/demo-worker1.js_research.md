# sources/storage-engines/sqlite/ext/wasm/demo-worker1.js

## Purpose

`demo-worker1.js` is a lower-level demonstration and test script for `sqlite3-worker1.js`. Unlike the promiser demo, it shows the raw message-passing mechanics needed to coordinate worker requests and asynchronous responses.

## Important APIs, Types, and Functions

- `SW = new Worker("jswasm/sqlite3-worker1.js")`: worker instance under test.
- `DbState.id`: records the active database ID returned by `open`.
- `MsgHandlerQueue`: FIFO callback queue keyed by generated `messageId` values.
- `runOneTest(eventType, eventArgs, callback)`: constructs a worker message with type, args, dbId, messageId, and departure time.
- `dbMsgHandler`: handlers for `open`, `exec`, `export`, `error`, and callback row messages such as `resultRowTest1`.
- `runTests()` and `runTests2()`: open sequencing and post-open test sequence.
- `SW.onmessage`: central dispatcher for readiness, queued responses, error messages, and callback result rows.

## Control Flow

The script creates a worker immediately and waits for a `sqlite3-api` message with result `worker1-ready`. On readiness it clears the loading spinner and calls `runTests()`. `runTests()` posts an `open` command and, with `waitForOpen` enabled, delays `runTests2()` until the open callback has set the `dbId`.

`runTests2()` posts a fixed sequence of worker commands: create/insert, query arrays, query objects, intentional SQL error, follow-up query to prove queue recovery, callback-based row streaming, multi-statement row mode selection, delete, count, export, and two closes. Responses with `messageId` shift one callback off `MsgHandlerQueue`; errors with `messageId` route through `dbMsgHandler.error`.

## State and Persistence

Worker-side database state persists for the life of the worker and the open DB. Main-thread state is `DbState.id`, the message handler queue, counters inside callback functions, and visible log DOM nodes. The database filename is `testing2.sqlite3`; close commands use `{unlink:true}` to remove it at the end.

## Dependencies and Integration Points

The demo depends on `jswasm/sqlite3-worker1.js`, `SqliteTestUtil`, `sqlite3TestModule`, the browser Worker API, `performance.now()`, and a `#test-output` element. It directly validates the worker API contract: readiness message, db IDs, message IDs, callback names, exported database payload shape, and error routing.

## Risks and Edge Cases

- The FIFO queue assumes worker messages for queued commands arrive in the same order as posted. The comments call out that errors can otherwise disrupt queue handling.
- If `waitForOpen` is disabled and open fails, all queued post-open work can fail because the messages cannot be canceled after posting.
- Callback dispatch by string name requires the worker response to match keys in `dbMsgHandler`.
- The first close unlinks the database; the second close tests no-op behavior but can mask bugs if the first close did not actually release state.

## Test Signals

Expected signals include the `worker1-ready` startup event, `open` returning `testing2.sqlite3`, a populated `dbId`, expected rows and column names for array/object modes, a handled intentional error with queue recovery, `resultRowTest1.counter === 3`, exported `Uint8Array` with SQLite MIME type and nontrivial length, first close returning a filename, and second close returning no filename.
