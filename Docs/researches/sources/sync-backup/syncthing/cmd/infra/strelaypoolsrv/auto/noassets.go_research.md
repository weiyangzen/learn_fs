# sources/sync-backup/syncthing/cmd/infra/strelaypoolsrv/auto/noassets.go

Purpose: build-tagged stub for relay pool server assets when building with `noassets`.

Important APIs/types/functions: build constraint `//go:build noassets`; `Assets() map[string]assets.Asset` returns nil.

Control flow: when the `noassets` tag is active, this file is compiled instead of relying on generated asset content, allowing static analysis or lightweight builds that do not require embedded GUI files.

State and persistence behavior: no state. It deliberately provides no assets at runtime.

Dependencies/integration: imports `github.com/syncthing/syncthing/lib/assets` for the return type and aligns with DeepSource `noassets` build tag plus build tooling that can avoid asset generation.

Risks/test signals: binaries built with `noassets` will not serve relay pool GUI assets through this package. Signal is successful package compilation with `-tags noassets` and expected nil asset map behavior.
