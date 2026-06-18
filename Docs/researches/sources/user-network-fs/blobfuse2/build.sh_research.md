<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/build.sh -->
# sources/user-network-fs/blobfuse2/build.sh

Purpose: local build helper for producing the main `blobfuse2` binary or the health monitor `bfusemon` binary. It selects fuse2, fuse3/default, or health-monitor builds based on the first argument.

Important APIs/types/functions: shell argument `$1`, `go version`, environment variables `CGO_ENABLED=1` and `GOTOOLCHAIN=local`, `go build -tags fuse2 -o blobfuse2`, `go build -o bfusemon ./tools/health-monitor/`, and default `go build -o blobfuse2`.

Control flow: print the Go version, force CGO and local toolchain use for FIPS-sensitive packaging, then branch on `$1`. `fuse2` removes old binary/source-directory artifacts and builds with the `fuse2` tag. `health` removes `bfusemon` and builds the health monitor tool. Any other argument builds the default fuse3-capable Blobfuse2 binary.

State/persistence behavior: writes `blobfuse2` or `bfusemon` in the repository root and removes old `blobfuse2`, `bfusemon`, or `azure-storage-fuse` paths before some builds. It intentionally prevents Go's automatic toolchain download so package builds do not silently switch to an upstream non-FIPS toolchain.

Dependencies/integration: depends on the installed local Go toolchain, CGO-capable C build environment, fuse build tags, and the `tools/health-monitor` package. It is used by release/build pipelines and local developer workflows.

Risks/test signals: destructive `rm -rf azure-storage-fuse` is safe in the release clone layout but risky if run from an unexpected directory. There is no `set -e`, so future multi-command edits could mask failures. The direct signal is whether `go build` exits successfully and the expected binary appears.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/build.sh -->
