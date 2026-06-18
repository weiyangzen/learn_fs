<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/Makefile -->
# sources/object-store/minio-mc/Makefile

## Purpose
Primary developer/CI automation for building, verifying, testing, cross-compiling, linting, installing, cleaning, and producing hotfix artifacts for MinIO client.

## Important APIs, types, and functions
Targets include `build`, `checks`, `getdeps`, `crosscompile`, `verifiers`, `vet`, `lint`, `lint-fix`, `test`, `test-race`, `verify`, `install`, `docker`, `hotfix`, `hotfix-push`, `docker-hotfix`, `docker-hotfix-push`, and `clean`. Variables derive GOPATH, LDFLAGS, GOOS/GOARCH, VERSION, TAG, and golangci path.

## Control flow
Default `all` builds. `build` checks dependencies then compiles with kqueue tag, trimpath, static CGO disabled, and generated ldflags. Test targets compose verifiers, builds, unit tests, race tests, and full functional tests. Hotfix targets rewrite version/ldflags, sign, checksum, and push artifacts.

## State and persistence behavior
Writes `mc`, GOPATH installs, release/hotfix artifacts, Docker images, and removes generated files on clean. It does not modify source except lint-fix via external tool.

## Dependencies and integration points
Calls build scripts, Go toolchain, golangci-lint, Docker, minisign, sha256sum, scp, and functional tests.

## Risks and test signals
Hotfix push embeds production host paths and credentials. `go install tool` depends on toolchain support. CI signals are `make`, `make test-race`, `make verify`, and `make crosscompile`.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/Makefile -->
