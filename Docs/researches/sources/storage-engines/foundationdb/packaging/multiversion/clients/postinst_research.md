<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/multiversion/clients/postinst -->
# Research: sources/storage-engines/foundationdb/packaging/multiversion/clients/postinst

## Purpose
Debian-style postinstall hook for multiversion client packages.

## Important APIs, Types, And Functions
Creates CMake and pkg-config directories if needed, then registers `fdbcli` as the master `update-alternatives` entry `fdbclients` with slaves for backup/restore/dr tools, `libfdb_c.so`, pkg-config metadata, CMake config, and headers.

## Control Flow
Runs after package unpack; directory creation precedes one large `update-alternatives --install` command using version/build-time placeholders and priority.

## State And Persistence Behavior
Persists alternatives symlinks under `/usr/bin`, `/usr/<lib>/`, `/usr/include/foundationdb`, and alternatives database state.

## Dependencies And Integration Points
Depends on Debian `update-alternatives`, configured `@LIB_DIR@`, `@FDB_VERSION@`, `@FDB_BUILDTIME_STRING@`, and package install layout under `/usr/lib/foundationdb-*`. Enables multiple installed FoundationDB client versions to coexist while one version owns public command/library/header paths.

## Risks And Edge Cases
Directory creation lacks `-p` and unquoted pkg-config mkdir, so parent existence and whitespace assumptions matter. A failed alternatives command can leave package installed but public client links absent.

## Test Signals
Validated by package install/upgrade/remove tests checking alternatives registration and command resolution.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/multiversion/clients/postinst -->
