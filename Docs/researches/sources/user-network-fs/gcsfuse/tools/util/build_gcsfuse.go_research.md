# sources/user-network-fs/gcsfuse/tools/util/build_gcsfuse.go

Purpose: helper library for integration tests to build gcsfuse and mount helper binaries into a destination directory.

Important APIs/types/functions: `BuildGcsfuse` and internal `buildBuildGcsfuse`.

Control flow: builds the `tools/build_gcsfuse` helper into a temp path using isolated GOPATH/GOCACHE, locates the gcsfuse module source via `go/build.Import`, then runs the helper with source dir, destination dir, and version `0.0.0`.

State/persistence behavior: creates temporary build directories and writes binaries/layout into the supplied destination directory.

Dependencies/integration: used by integration setup when tests do not use installed or prebuilt gcsfuse. Requires Go toolchain and module source to be discoverable.

Risks/test signals: `go/build.Import` reflects GOPATH-era lookup behavior and can be fragile under unusual module/workspace setups. Build errors include combined command output.
