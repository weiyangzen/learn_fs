# sources/user-network-fs/rclone/fs/rc/js/main.go

## Purpose
This Go source is the browser/WebAssembly entry point for exposing selected rclone remote-control functionality to JavaScript. It is built only for the `js` target and imports the RC registry plus a small set of rclone capabilities: operations, sync, and the memory backend.

## Important APIs, Types, and Functions
- `main` validates the browser environment, captures `document` and `JSON`, installs `globalThis.rc` as a `js.FuncOf(rcCallback)`, resolves `rcValidResolve`, and then blocks forever.
- `rcCallback(this js.Value, args []js.Value) interface{}` is the exported JavaScript call bridge. It expects exactly two arguments: method name and null/object input.
- `errorValue(method string, in js.Value, err error) js.Value` maps Go errors into a JS object with `status`, `error`, `input`, and `path`, using RC/FS error classification.
- `getElementById`, `time`, and `paramToValue` are local helpers; `paramToValue` is currently a stub returning an empty `js.Value`.

## Control Flow
Startup checks `js.Global`, `document`, and `JSON`; failures are fatal because the module is browser-oriented. Calls enter through `rcCallback`, stringify JS object input with `JSON.stringify`, unmarshal into `rc.Params`, look up `rc.Calls.Get(method)`, invoke the registered Go RC function synchronously with `context.Background`, then reshape the returned `rc.Params` into `map[string]interface{}` for `js.ValueOf`.

## State and Persistence
The file keeps browser globals in package variables `document` and `jsJSON`. It does not persist data directly; invoked RC functions may mutate state, files, or remotes depending on what has been registered. The installed `globalThis.rc` function remains live for the lifetime of the WASM process.

## Dependencies and Integration Points
It depends on `syscall/js`, `encoding/json`, `fs/rc`, and implicitly on imported packages that register RC calls in `init`. The build imports only the memory backend, so browser use is constrained unless more backends are uncommented or added. It integrates with `wasm_exec.js` and host JavaScript through `rcValidResolve`.

## Risks and Edge Cases
The RC call is synchronous and uses `context.Background`, so cancellation, deadlines, and request-scoped auth are absent. Input objects must survive JSON stringification; functions, cyclic structures, and unsupported JS values fail or lose information. `call.NoAuth` and HTTP auth checks are not enforced here, so the browser embedding must treat the exposed `rc` function as privileged.

## Test Signals
No dedicated tests are present for this file in the subset. Behavior is indirectly coupled to RC registry and parameter tests, but browser/WASM integration needs manual or browser-driven validation.
