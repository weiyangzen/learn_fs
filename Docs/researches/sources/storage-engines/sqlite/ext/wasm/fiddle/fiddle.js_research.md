# sources/storage-engines/sqlite/ext/wasm/fiddle/fiddle.js

## Purpose

`fiddle.js` is the main-thread entry point for the SQLite WASM fiddle application. It sets up browser storage-backed UI configuration, creates the worker, dispatches worker messages, manages views, routes shell input/output, handles import/export controls, and optionally integrates `jquery.terminal`.

## Important APIs, Types, and Functions

- Internal `storage` module: wrapper around `localStorage`, `sessionStorage`, or a transient in-memory fallback with a per-app key prefix.
- `window.SqliteFiddle` / `SF`: main app object.
- `SF.config`: UI preferences such as auto-scroll, auto-clear, echo-to-console, side-by-side layout, and input/output swapping.
- `SF.echo()`: writes output to the textarea and optional terminal.
- `SF.addMsgHandler()`, `runMsgHandlers()`, `clearMsgHandlers()`, and `wMsg()`: worker message dispatch and send helpers.
- `SF.resetDb()`, `storeConfig()`, `setMainView()`, `toggleAbout()`, and `dbExec()`.
- `effectiveHeight()`, `debounce()`, and `SF.ForceResizeKludge()`: layout helpers.
- `self.onSFLoaded()`: delayed UI wiring after the worker reports readiness.

## Control Flow

The script initializes the storage wrapper, restores stored config into `SF.config`, starts `new Worker("fiddle-worker.js" + location.search)`, and wires message handlers for stdout/stderr, SQLite version, WASM info, module load status, and `fiddle-ready`. On `fiddle-ready`, it runs `onSFLoaded()`.

`onSFLoaded()` unhides the app, establishes the active view, wires reset/about/clear/execute buttons, maps Ctrl-Enter and Shift-Enter to shell execution, tracks working state for execute and interrupt buttons, binds checkboxes to CSS targets and persisted config, adds canned command buttons, wires database export/import controls, builds the examples dropdown, optionally initializes the terminal view, executes any `?sql=` URL parameter, enables resize handling, and exposes `globalThis.fiddle`.

Export disables mutating controls, asks the worker for `db-export`, builds a `Blob`, and auto-clicks a download link. Import reads a selected file as an `ArrayBuffer`, transfers it to the worker with an `open` message, and re-enables controls on load/error/abort.

## State and Persistence

Persistent UI state is stored under `sqlite3-fiddle-config` using the storage wrapper and a prefix derived from project config or `window.location.pathname`. If browser storage is unavailable, settings are transient. Runtime state includes `SF.worker`, handler maps, cached DOM references, output textarea content, terminal instance, active view, pending clear flag, and temporary object URLs for exports. Database state itself lives in the worker.

## Dependencies and Integration Points

The script depends on the DOM structure of the fiddle page, browser Worker/FileReader/Blob/ObjectURL APIs, optional `window.jQuery.terminal`, and `fiddle-worker.js` message types. It integrates with the worker protocol for `stdout`, `stderr`, `sqlite-version`, `wasm-info`, `module`, `fiddle-ready`, `working`, and `db-export`, and sends `shellExec`, `db-reset`, `interrupt`, `db-export`, and `open`.

## Risks and Edge Cases

- In the module status handler there is a typo-like check `f.ui.progres` while later code uses `f.ui.progress`, so progress value/max updates may never run.
- `preStartWork()` is called even when `dbExec(null)` is used at startup, which can briefly toggle working UI before the worker receives a no-op shell command.
- Import/export disabling is separate from shell `working` state and can race if operations overlap in unexpected order.
- Storage keys are origin scoped with a path/project prefix; multiple apps on the same origin can still coexist only if prefixes remain unique.
- Terminal integration modifies formatter behavior globally in `jquery.terminal`.
- The layout workaround manually sizes views and may need browser-specific testing.

## Test Signals

Tests should verify config restore/store, worker startup and `fiddle-ready`, module status visibility, stdout/stderr echo, version link generation, WASM info text and terminal prompt updates, Ctrl/Shift-Enter execution, selection-only execution, working state toggles, checkbox CSS/config sync, examples dropdown execution, export download object URL cleanup, file import transfer to worker, terminal mode toggle, and `?sql=` startup execution.
