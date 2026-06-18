# sources/sync-backup/syncthing/buf.gen.yaml

Purpose: Buf code generation configuration for Syncthing protobuf definitions.

Important APIs/types/functions: `version: v2`; managed mode is enabled with `go_package_prefix` override set to `github.com/syncthing/syncthing/internal/gen`. The Go plugin uses remote `buf.build/protocolbuffers/go:v1.35.1`, outputs into `.`, and sets `module=github.com/syncthing/syncthing`. Input directory is `proto`.

Control flow: `buf generate` reads `proto` definitions, applies managed Go package settings, and writes generated Go files under paths consistent with the module prefix.

State and persistence behavior: generation mutates checked-in generated files under the repository, especially `internal/gen`.

Dependencies/integration: used by `build.go proto` and `updateDependencies`; relies on Buf and the remote protocolbuffers Go plugin.

Risks/test signals: plugin version drift changes generated code. Wrong prefix or module option can put code in unexpected packages. Signal is reproducible `buf generate` output and successful Go builds importing `internal/gen`.
