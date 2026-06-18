# sources/sync-backup/syncthing/buf.yaml

Purpose: Buf module, lint, and breaking-change policy for Syncthing protobuf definitions.

Important APIs/types/functions: `version: v2`; module path `proto` with name `github.com/syncthing/syncthing`; lint uses `STANDARD`; breaking checks use `WIRE_JSON`.

Control flow: Buf commands load the `proto` module, apply standard lint rules, and check compatibility at wire and JSON levels when a breaking-change baseline is supplied.

State and persistence behavior: no runtime state. It defines validation constraints for protobuf source evolution.

Dependencies/integration: paired with `buf.gen.yaml`, `build.go proto`, generated Go code, and CI or developer commands that run Buf.

Risks/test signals: `WIRE_JSON` focuses compatibility on encoded contracts but may not catch every generated-API compatibility concern. Signal is Buf lint/generate passing after proto changes.
