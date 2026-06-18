# sources/user-network-fs/rclone/fs/rc/js/serve.go

## Purpose
This is a development-only helper server for serving the WASM demo/current directory over HTTP. The `//go:build none` tag prevents it from participating in normal builds.

## Important APIs, Types, and Functions
- `main` registers MIME types for `.wasm` and `.js`, serves the current directory with `http.FileServer(http.Dir("."))`, and listens on `:3000`.

## Control Flow
The helper process creates a default mux, attaches static file serving at `/`, prints the local URL, and blocks in `http.ListenAndServe`.

## State and Persistence
No persistent state is managed. It exposes files from the current working directory at runtime.

## Dependencies and Integration Points
It uses only Go standard-library packages: `fmt`, `log`, `mime`, and `net/http`. It pairs with `main.go` and `wasm_exec.js` during local browser testing.

## Risks and Edge Cases
Serving `.` can expose any local files in the working directory. The fixed port `3000` may conflict with other services. It lacks auth, TLS, directory restrictions beyond the process CWD, and production hardening, which is acceptable for a build-excluded development utility.

## Test Signals
No automated tests are present. The build tag itself is the primary safety signal that this does not enter normal binaries.
