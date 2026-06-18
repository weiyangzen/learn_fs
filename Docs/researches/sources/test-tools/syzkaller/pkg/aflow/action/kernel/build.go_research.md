# sources/test-tools/syzkaller/pkg/aflow/action/kernel/build.go

## Purpose

`build.go` defines the kernel build action and reusable `BuildKernel` helper. It turns a kernel source tree and config into a cached object directory containing the kernel image, vmlinux, compile database, and retained generated/source files.

## Important APIs, Types, and Functions

`Build = aflow.NewFuncAction("kernel-builder", buildKernel)`. `buildArgs` contains target, source, commit, and config; `buildResult.KernelObj` is the output directory. `BuildKernel` writes `.config`, adjusts config with `scripts/config`, invokes `make`, extracts root-cause build errors, and optionally cleans intermediate files. `cmdlineRe` preserves existing ARM64 command-line config when appending required boot args.

## Control Flow

The helper writes the config to the build directory, disables x32 and enforces gzip for amd64, appends GCE serial/root command-line defaults for arm64, runs `scripts/config`, derives the image and make arguments, builds the image and `compile_commands.json`, and wraps root-cause build failures as `aflow.FlowError`. If cleanup is enabled, it walks the build directory and deletes files that are not the kernel image, vmlinux, compile database, directories, or source files.

## State and Persistence Behavior

The action uses `ctx.Cache("build", desc, populate)` where `desc` is keyed by kernel commit and config hash. Cached build directories are reference-counted by the aflow cache and released on context close.

## Dependencies and Integration Points

It depends on syzkaller `build`, `codesearch`, `hash`, `osutil`, and target metadata. The build output feeds VM reproduction, code search indexing, and patch testing. It assumes LLVM toolchain defaults and ccache.

## Risks and Edge Cases

Kernel builds are long-running and environment-sensitive. Config rewriting is target-specific and only handles amd64/arm64 special cases. Cleanup must preserve generated source files for code search while reclaiming space; overly broad deletion could harm later tooling. `build.ExtractRootCause` classification determines whether users see actionable root-cause information.

## Test Signals

No direct unit tests are present. Signals come from workflow registration and real kernel build integration runs.
