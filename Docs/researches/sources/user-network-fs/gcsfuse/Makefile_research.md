## sources/user-network-fs/gcsfuse/Makefile

Purpose: Provides common developer and release automation targets for gcsfuse.

Important APIs/types/functions: variables `CSI_VERSION`, `GCSFUSE_VERSION`, `GOLANG_VERSION`, `BUILD_ARM`, `STAGINGVERSIONPREFIX`, fallback `STAGINGVERSION`, and `PROJECT`. Targets include `generate`, `imports`, `fmt`, `vet`, `lint`, `build`, `buildTest`, `install`, `test`, cleanup targets, `build-csi`, and `e2e-test`.

Control flow: default target `build` chains `lint -> vet -> fmt -> imports -> generate`. Formatting runs goimports, go mod tidy, and gofmt. Tests use `CGO_ENABLED=0` and split internal cache tests with `-p 1`. `build-csi` submits Cloud Build with substitutions. `e2e-test` queries GCE metadata for zone/region and runs improved integration tests.

State and persistence: modifies generated files/import formatting/module files during fmt paths; build/install/test create normal Go artifacts; cleanup removes generated config files; Cloud Build and e2e interact with Google Cloud resources.

Dependencies and integration points: requires Go tools, goimports, golangci-lint, git, gcloud, metadata server for e2e, and project-specific build/integration scripts.

Risks: many targets mutate the tree before checking; `clean-gen` deletes generated `cfg/config.go` and `cfg/config_test.go`; `lint` depends on `master` revision availability; `e2e-test` assumes GCE metadata. `STAGINGVERSION` prefix logic is designed for CSI compatibility and should not be casually changed.

Test signals: Make targets are themselves verification signals, especially `make fmt`, `make test`, `make build`, and cloud/e2e logs.
