# sources/test-tools/syzkaller/tools/syz-make/make.go

## Purpose
`syz-make` prints shell `export` assignments used by syzkaller Makefiles to derive native/cross build variables and a conservative parallelism setting.

## Important APIs, types, and functions
- `main` calls `impl`, prints `SYZERROR` and exits nonzero on failure, otherwise emits each `Var` as `export NAME=value\n`.
- `Var` is the simple name/value output model.
- `impl` resolves `HOSTOS`, `HOSTARCH`, `TARGETOS`, `TARGETARCH`, and `TARGETVMARCH` from environment variables with runtime fallbacks, validates `targets.Get`, and derives compiler/linker flags from `sys/targets`.
- `or` is the environment fallback helper.

## Control flow
The tool computes host/target defaults, looks up target metadata, starts parallelism at CPU count, then reduces it for CI, OpenBSD, and low-memory hosts. The memory limiter keeps `NCORES*NCORES <= memoryGiB` to account for nested Make and Go build parallelism.

## State and persistence behavior
No files are read or written. Output is stdout shell text intended to be evaluated by Make/shell. The only process state read is environment variables, OS/architecture, CPU count, and memory size.

## Dependencies and integration points
`pkg/osutil.SystemMemorySize` supplies RAM size. `sys/targets` supplies compiler names, flags, executable suffixes, broken compiler markers, and build OS. The Makefile consumes the emitted variables.

## Risks and edge cases
Values are printed without shell escaping, so target metadata and environment-derived values are expected to be safe tokens. `NATIVEBUILDOS` is emitted twice with the same value. If system memory cannot be determined, CPU parallelism may still be too aggressive on memory-constrained systems. CI and OpenBSD intentionally force single Make parallelism.

## Test signals
No direct tests here. Good validation includes running under representative env var combinations, unknown target pairs, CI/OpenBSD paths, and low-memory hosts.
