## sources/test-tools/syzkaller/sys/fuchsia/layout/fidl_mappings.go

Purpose: maps Fuchsia FIDL library names to build-output paths used by the fidlgen tool.

Important APIs/types/functions: `FidlLibrary`, `AllFidlLibraries`, `dirName`, `PathToJSONIr`, and `PathToCompiledDir`.

Control flow: `dirName` joins library components with dots. `PathToCompiledDir` builds the relative `fidling/gen/sdk/fidl/<library>` directory. `PathToJSONIr` appends `<library>.fidl.json` under that directory.

State and persistence: static library list only. No writes.

Dependencies/integration: consumed by `sys/fuchsia/fidlgen/main.go`.

Risks: the list and path layout must match the Fuchsia build tree. Adding/removing FIDL libraries requires updating `AllFidlLibraries`.

Test signals: no direct tests; failures surface in Fuchsia go generate workflows.
