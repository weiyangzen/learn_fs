# sources/user-network-fs/blobfuse2/.github/workflows/arm-ci.yml

## Purpose
This workflow cross-compiles Blobfuse2 for ARM32/armhf with libfuse3 and verifies the resulting binary under qemu.

## Important APIs, Types, and Functions
It uses `actions/checkout@v6`, apt packages for qemu and ARM cross compilation, `wget` plus `dpkg-deb` to extract armhf `libfuse3-dev` and runtime packages, `actions/setup-go@v6`, and `go build`.

## Control Flow
The workflow runs on manual dispatch, pushes to `main`, and pull requests to `main`. It installs qemu and `arm-linux-gnueabihf` tools, downloads Ubuntu armhf libfuse packages, sets `GOOS=linux`, `GOARCH=arm`, `GOARM=7`, `CGO_ENABLED=1`, `CC`, `CGO_CFLAGS`, and `CGO_LDFLAGS`, builds `blobfuse2-arm`, then runs `blobfuse2-arm --version` through `qemu-arm`.

## State and Persistence Behavior
All state is workspace-local under `deps/` and the built `blobfuse2-arm` artifact. No artifacts are uploaded and no branches are mutated.

## Dependencies and Integration Points
It integrates Go CGO compilation with libfuse headers and ARM qemu runtime. The job validates a platform not covered by normal amd64 Linux CI.

## Risks and Edge Cases
The libfuse URLs point to old Ubuntu release package paths and can break if unavailable. It verifies only `--version`, not mounting. Cross-linking depends on extracted library paths and qemu sysroot compatibility. Unit tests are explicitly omitted.

## Test Signals
Signals are successful armhf package extraction, `file blobfuse2-arm` showing ARM output, and qemu returning version output without missing loader or libfuse errors.
