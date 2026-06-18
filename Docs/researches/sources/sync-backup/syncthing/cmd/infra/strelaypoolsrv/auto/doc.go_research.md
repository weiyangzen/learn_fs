# sources/sync-backup/syncthing/cmd/infra/strelaypoolsrv/auto/doc.go

Purpose: package documentation and go-generate directive for generated relay pool server web assets.

Important APIs/types/functions: `//go:generate go run ../../../../script/genassets.go -o gui.files.go ../gui` and package declaration `auto`.

Control flow: `go generate` for this package invokes the repository asset generator to embed files from `cmd/infra/strelaypoolsrv/gui` into `gui.files.go`.

State and persistence behavior: generation writes or updates `gui.files.go` in this package. The source file itself has no runtime state.

Dependencies/integration: used by `build.go rebuildAssets`, which generates this package alongside API GUI assets. Consumers import `auto` to access generated assets.

Risks/test signals: stale generated assets can occur if `go generate` is not run after GUI changes. Signal is generated `gui.files.go` present and builds succeeding without the `noassets` tag.
