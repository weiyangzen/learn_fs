<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/fdb/fdb_freebsd.go -->
# sources/storage-engines/foundationdb/bindings/go/src/fdb/fdb_freebsd.go

Purpose: platform-specific cgo flags for FreeBSD builds.

Important content: package `fdb`; `CFLAGS` uses `/usr/local/include`; `LDFLAGS` uses `/usr/local/lib`.

Control flow/state: no runtime logic and no persistent state.

Dependencies and integration: participates in cgo package compilation based on `_freebsd.go` filename. Supplies include/library search paths for the FoundationDB C client.

Risks: no rpath is set, so runtime loader configuration must find `libfdb_c`. Assumes conventional local install paths. Build failures will appear as missing headers or link libraries.

Test signals: validated by FreeBSD build/link coverage only.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/fdb/fdb_freebsd.go -->
