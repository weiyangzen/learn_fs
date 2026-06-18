<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/fdb/fdb_windows.go -->
# sources/storage-engines/foundationdb/bindings/go/src/fdb/fdb_windows.go

Purpose: Windows-specific cgo flags for the Go binding.

Important content: package `fdb`; `CFLAGS` points to `C:/Program Files/foundationdb/include`; `LDFLAGS` points to `C:/Program Files/foundationdb/bin` and links `-lfdb_c`.

Control flow/state: no runtime logic or persistence.

Dependencies and integration: selected by `_windows.go` suffix during Go builds. Supplies default FoundationDB installer paths for cgo.

Risks: assumes installation path and architecture. Spaces in paths are quoted, but custom installs need external cgo flags. Runtime DLL search must find `fdb_c.dll`.

Test signals: Windows build/link and runtime smoke tests validate this file.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/fdb/fdb_windows.go -->
