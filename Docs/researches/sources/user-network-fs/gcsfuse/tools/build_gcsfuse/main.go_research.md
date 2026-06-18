<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/build_gcsfuse/main.go -->
# sources/user-network-fs/gcsfuse/tools/build_gcsfuse/main.go

Purpose: Release/build helper that compiles gcsfuse and its mount helper into a target filesystem hierarchy suitable for packaging or installation.

Important APIs, types, and functions: `buildBinaries(dstDir, srcDir, version, arch, buildArgs)` creates `bin`/`sbin`, constructs temporary `GOPATH` and `GOCACHE`, symlinks source into GOPATH layout, runs `go build` for `github.com/googlecloudplatform/gcsfuse/v3` and `tools/mount_gcsfuse`, injects `common.gcsfuseVersion` via ldflags for the main binary, and creates Linux `mount.fuse.gcsfuse` symlink. `run` parses `--arch` via `pflag` and positional `src_dir dst_dir version [build args]`.

Control flow: `main` sets logging and exits nonzero on `run` error. `run` validates at least three positional args, then delegates to `buildBinaries`. `buildBinaries` prepares directories, environment, mount helper naming, build command arguments, environment variables (`GO111MODULE=auto`, `CGO_ENABLED=0`, `GOARCH`, GOPATH/GOCACHE), and then builds each target.

State and persistence behavior: Writes binaries and symlinks under `dstDir`. Temporary GOPATH/GOCACHE directories are removed by deferred cleanup. It reads `PATH`, source tree, Go toolchain, and runtime `GOROOT`.

Dependencies and integration points: Used by release scripts, package Dockerfiles, and local source installation paths. Depends on Go 1.20+ for `go build -C`, `spf13/pflag`, runtime OS/arch, and the gcsfuse module path.

Risks and test signals: Destination `bin`/`sbin` creation fails if directories already exist. The command forces `GO111MODULE=auto` and `CGO_ENABLED=0`, which may not match future build needs. Error wrapping detects unsupported `-C` to suggest Go upgrade. Tests verify version stamping by building and running `gcsfuse --version`/`-v`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/build_gcsfuse/main.go -->
