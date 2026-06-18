# sources/test-tools/syzkaller/executor/kvm_gen.cc

Purpose: Small build-time generator that emits C string byte arrays from linked assembly symbol ranges.

Important APIs and control flow: `PRINT(x)` declares external `x` and `x_end` byte symbols and calls `print`. `print` writes `const char name[] = "\x.."` for every byte in `[start, end)`. `main` prints a generated-file banner and selects amd64 or ppc64le symbol sets based on `GOARCH_amd64`/`GOARCH_ppc64le`.

State and dependencies: stateless command-line program using `stdio`. It relies on the linker preserving assembly symbol addresses and on architecture macros supplied by `go generate`.

Integration points: invoked by `gen_linux_amd64.go` and `gen_linux_ppc64le.go`; output is checked into `kvm_*.S.h`.

Risks and tests: missing `_end` symbols, wrong architecture macros, or assembler/linker changes can generate invalid or empty arrays. Tests are generated-header diffs and runtime KVM tests that consume the arrays.
