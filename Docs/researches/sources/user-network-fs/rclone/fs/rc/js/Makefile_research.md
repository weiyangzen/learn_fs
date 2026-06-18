# Research: sources/user-network-fs/rclone/fs/rc/js/Makefile

## sources/user-network-fs/rclone/fs/rc/js/Makefile

Purpose: small developer Makefile for building and serving the rc WebAssembly JavaScript demo. Targets are `build` and `serve`.

Control flow is delegated to make: `build` runs `GOARCH=wasm GOOS=js go build -o rclone.wasm`; `serve` depends on `build` and runs `go run serve.go`. State/persistence is the generated `rclone.wasm` artifact in the working directory and any local server process launched by `serve`. Dependencies include Go’s wasm target and a local `serve.go` file outside this listed scope. Integration point is `loader.js`, which expects `rclone.wasm` and `wasm_exec.js` to be available. Risks include generated binary churn, implicit current package build target, no cleanup target, and missing `serve.go`/wasm support causing make failures. No tests directly cover this file.
