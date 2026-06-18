# sources/test-tools/syzkaller/pkg/csource/build.go

This Go file builds generated C/C++ reproducers and formats generated C source. Public functions are `Build`, `BuildNoWarn`, `BuildExecutor`, and `Format`; the private `build` routine holds compiler selection and invocation.

`build` creates a temporary `syz-executor` binary path, assembles target macros (`GOOS_`, `GOARCH_`, `HOSTGOOS_`), selects C or C++ compiler/flags from `targets.Get`, streams generated C through stdin when no source file is supplied, and returns detailed source/output/invocation diagnostics on failure. `BuildNoWarn` relaxes compiler warnings for old reproducers or unknown compilers, while `BuildExecutor` compiles `executor/executor.cc` with `-O0` for tests and registers cleanup with `testing.T`.

State is mostly transient: temporary output files are created and removed on failure or test cleanup. Dependencies are `osutil.Command`, syzkaller target metadata, Go runtime host OS, and clang-format. `Format` pipes source through `clang-format` using an embedded Linux-kernel-friendly style.

Integration points include csource tests, reproducers, bisection, and executor test builds. Risks include target compiler availability, stale target flags, warning policy differences, leaked temp binaries outside test cleanup, and formatter absence. Test signals are indirect in `csource_test.go`, where generated sources are built through `Build`.
