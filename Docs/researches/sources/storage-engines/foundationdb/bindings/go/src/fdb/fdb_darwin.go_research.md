<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/fdb/fdb_darwin.go -->
# sources/storage-engines/foundationdb/bindings/go/src/fdb/fdb_darwin.go

Purpose: platform-specific cgo flags for macOS builds of the Go binding.

Important content: package `fdb`; cgo `CFLAGS` adds `/usr/local/include`; cgo `LDFLAGS` adds `/usr/local/lib` and runtime path `/usr/local/lib`.

Control flow/state: no Go runtime logic, no persistence.

Dependencies and integration: affects cgo compilation/linking for files importing `C` in the same package. It assumes FoundationDB headers and `libfdb_c` are installed in Homebrew/default `/usr/local` style locations.

Risks: Apple Silicon installations often use `/opt/homebrew`, so this may not locate libraries without external flags. Runtime rpath is convenient but can mask version mismatches. It has no build tag in the file body, so platform selection relies on `_darwin.go` suffix.

Test signals: only build/link tests on Darwin validate this file.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/fdb/fdb_darwin.go -->
