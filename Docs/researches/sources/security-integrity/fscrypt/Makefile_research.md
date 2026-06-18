# sources/security-integrity/fscrypt/Makefile

Purpose: central build, test, generation, lint, coverage, install, and tool-bootstrap logic for `fscrypt` and `pam_fscrypt`.

Important targets/variables: `VERSION`, `NAME`, `PAM_NAME`, `BIN`, `PAM_MODULE`, `CFLAGS`, `GO_LINK_FLAGS`, `VERSION_FLAG`, `FILES`, `GO_FILES`, `C_FILES`, `PROTO_FILES`. Build targets produce `bin/fscrypt` and `bin/pam_fscrypt.so`. `gen` runs protoc, `format` runs goimports and clang-format, `lint` runs go vet/staticcheck/misspell/shellcheck, `test` runs `go test -p 1 ./...`, `test-setup` creates/mounts an ext4 image with encryption, `cli-test` runs sudo CLI tests, `coverage.out` merges per-package coverage, and install targets place binaries, PAM module/config, and bash completion.

Control flow: `default` builds binary and PAM module; `all` runs tools, generation, default, format, lint, and tests. Build commands add git tag or fallback version into `main.version`, apply `-trimpath` if supported, and pass C flags through cgo. Tool targets build Go helpers or download/copy `protoc` based on architecture.

State and persistence: writes under `bin`, `/tmp/fscrypt-image`, `/tmp/fscrypt-mount`, installation prefixes, coverage files, and generated protobuf files. `test-setup` uses sudo mount; `test-teardown` unmounts and deletes.

Dependencies and integration points: integrates Go modules, cgo, PAM, m4, protobuf, ext4 fscrypt support, shellcheck, staticcheck, misspell, goimports, clang-format, sudo, and CLI test scripts.

Risks: `TAG_VERSION := $(shell git describe --tags)` can fail noisily without tags. `test-setup` assumes sudo and loop mounts are available. Downloading `protoc` during builds requires network. Install paths default to `/usr/local` and may need root.

Test signals: Makefile targets are the CI contract and local developer entry points for build correctness, generated-file cleanliness, and integration test setup.
