## sources/security-integrity/libcap/go/Makefile

Purpose: builds and tests libcap's Go packages, Go example applications, and Go/C interoperability checks using a vendor symlink tree that mimics module import paths.

Important targets/variables: `IMPORTDIR`, `PKGDIR`, `DEPS`, `TESTS`, `vendor/modules.txt`, `vendor/.../psx`, `vendor/.../cap`, `good-names.go`, `PSXGOPACKAGE`, `CAPGOPACKAGE`, app targets `web`, `setid`, `gowns`, `captree`, `captrace`, tests `compare-cap`, `try-launching`, `psx-signals`, `mismatch`, `iaber`, `b210613`, `b215283`, `test`, `sudotest`, `install`, and `clean`.

Control flow: builds `../libcap/libcap.a` and `../libcap/libpsx.a`, creates a Go vendor tree with symlinks to `../cap` and `../psx`, generates and diffs `good-names.go` from `cap_names.h`, builds packages/apps with `CGO_ENABLED` selected by `CGO_REQUIRED`, runs `go vet`, executes package tests and helper binaries, and runs privileged tests under `$(SUDO)` for launcher/IAB/regression behavior.

State/persistence: creates vendor directories, stamp files, generated `good-names.go`, binaries, `go.sum`, and optional file capabilities on `web` when `RAISE_GO_FILECAP=yes`.

Dependencies/integration: GNU make, Go toolchain, cgo, libcap/libpsx static libs, top-level `Make.Rules`, `setcap`, `tcapsh-static`, sudo-capable environment for `sudotest`.

Risks: symlinked vendor layout is fragile under tools that rewrite vendor trees; some tests are privilege/kernel/runtime dependent; known older Go all-thread syscall bugs are handled by cgo fallback paths but can still affect results.

Test signals: `make -C go test`, `make -C go sudotest`, cgo and non-cgo matrix when `CGO_REQUIRED=0`, `good-names.go` diff, and successful `captree` install staging.
