# sources/storage-engines/sqlite/ext/wasm/common/SqliteTestUtil.js

## Purpose
This file provides browser/worker test bootstrap utilities for SQLite wasm test pages. It defines assertion helpers under `self.SqliteTestUtil` and an Emscripten module configuration object under `self.sqlite3TestModule`. The utilities support test counting, error assertions, URL argument parsing, module loading progress UI, stdout/stderr forwarding, and temporary sqlite3 API configuration.

## Important APIs, Types, and Functions
`SqliteTestUtil` exposes `counter`, `toBool(expr)`, `assert(expr, ...msg)`, `affirm(expr, msg)`, `mustThrow(f, msg)`, `mustThrowMatching(f, filter, msg)`, `throwIf(expr, msg)`, `throwUnless(expr, msg)`, and `processUrlArgs(str)`. The local `E()` and `EAll()` functions proxy `querySelector()` and `querySelectorAll()` and are used by the module status UI.

`sqlite3TestModule` provides `postRun`, `print`, `printErr`, `setStatus(text)`, `sqlite3ApiConfig`, and `initSqlite3()`. The default `sqlite3ApiConfig` sets `wasmfsOpfsDir: "/opfs"`.

## Control Flow
The file is an IIFE over `self`, so it works in window or worker-like globals. Assertion-style helpers increment `SqliteTestUtil.counter` for every check. `assert()` lazily chooses either global `abort` or a throwing fallback, then aborts/throws on failure. `affirm()` always throws on failure. `mustThrow()` and `mustThrowMatching()` execute a callback and require an exception, with matching by regex, predicate, or exact string.

`processUrlArgs()` defaults to `window.location.search.substring(1)` when no argument is supplied and a window search string exists. It strips fragments, splits on ampersands, decodes keys and values, and returns a prototype-less object; keys without values receive boolean `true`.

`sqlite3TestModule.setStatus()` lazily locates `#module-status`, `#module-progress`, and `#module-spinner`, ignores repeated text, advances progress on each status change, displays non-empty status text, and removes/hides progress UI when loading completes. `initSqlite3()` temporarily installs `self.sqlite3ApiConfig`, calls `self.sqlite3InitModule(this)`, and removes the global config in `finally()`.

## State and Persistence Behavior
State is transient test harness state: the assertion counter, cached abort function, cached status UI references, last status text/step, module `postRun` callbacks, and temporary `self.sqlite3ApiConfig`. It does not persist data or modify SQLite databases directly. The temporary config affects sqlite3 initialization only during `initSqlite3()`.

## Dependencies and Integration Points
The file depends on browser DOM APIs when status UI is used, `console.log/error`, optional global `abort`, `window.location`, and Emscripten's `sqlite3InitModule()` factory. It is used by test scripts in the same wasm common/test area and feeds `sqlite3ApiBootstrap()` indirectly through `sqlite3ApiConfig`. It works in workers for non-DOM paths because DOM access is delayed until `setStatus()`.

## Risks and Edge Cases
`setStatus()` assumes DOM elements exist before manipulating classes or text; tests without those IDs must avoid status UI or provide stubs. `assert()` may call `abort()` instead of throwing, which can terminate execution differently across environments. `processUrlArgs()` is simple and treats missing values as `true`; it does not preserve duplicate keys. `initSqlite3()` mutates global `self.sqlite3ApiConfig` temporarily, so concurrent initialization attempts with different configs could interfere.

## Test Signals
Tests should cover assertion counter increments, function and value truthiness via `toBool()`, abort/throw failure behavior, exception matching modes, URL parsing with encoded keys/values, flags, fragments, and no-window fallback, status UI transitions with repeated and final empty status, stdout/stderr forwarding, `postRun` preservation, and `initSqlite3()` installing/removing `sqlite3ApiConfig` around a mocked module factory.
