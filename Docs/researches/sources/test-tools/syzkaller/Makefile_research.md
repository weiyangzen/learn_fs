<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/Makefile -->
# sources/test-tools/syzkaller/Makefile research

Purpose: top-level syzkaller build, generation, formatting, lint, test, and presubmit orchestration.

Important APIs, types, and functions: key variables include host/target OS and arch triplets, `GOFLAGS` with revision ldflags, `CGO_ENABLED`, `GOBIN`, `TARGETGOOS`, and `TARGETGOARCH`. Targets build host tools (`syz-manager`, `syz-ci`, `syz-agent`, `syz-lore-relay`, `syz-repro`, `syz-db`, etc.), target tools/executor, generated syscall descriptions, Go/RPC/syscall generation, formatting, linting, architecture presubmits, race presubmits, and prerequisite installation.

Control flow: `tools/syz-make/make.go` computes environment settings consumed by Make. `all` builds host and target artifacts. `descriptions` installs/runs `syz-sysgen` and updates `.descriptions`. Presubmit targets compose generation, formatting checks, builds, lint, tests, multi-arch target builds, executor variants, dashboard tests, and race tests.

State and persistence: writes build artifacts under `bin/`, generated syscall files under `sys/gen`, executor generated headers, `.descriptions`, coverage files, and generated mocks/RPC code. `clean` removes core build/generated artifacts.

Dependencies and integration: depends on Go modules, C/C++ compilers, clang-format/tidy, flatc, ragel, goyacc, keep-sorted, golangci-lint, syz-linter plugin, kernel source trees for extraction/config targets, and CI wrappers.

Risks: the Makefile drives many generated artifacts, so partial toolchain differences can cause noisy diffs. `CGO_ENABLED=0` is the default except selected targets, which is important for Android/static compatibility. Architecture targets assume cross compilers and platform support discovered by `syz-make`.

Test signals: `make`, `make presubmit`, `make test`, `make lint`, `make generate`, and `make check_diff` are the primary signals. CI maps directly onto many of these presubmit subtargets.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/Makefile -->
