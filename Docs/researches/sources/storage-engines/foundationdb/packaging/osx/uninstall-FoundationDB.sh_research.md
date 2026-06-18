<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/osx/uninstall-FoundationDB.sh -->
# Research: sources/storage-engines/foundationdb/packaging/osx/uninstall-FoundationDB.sh

## Purpose
Manual macOS uninstall script for FoundationDB binaries, libraries, headers, bindings, LaunchDaemon, and receipts.

## Important APIs, Types, And Functions
Removes installed executables, `libfdb_c.dylib`, headers, backup agent directory, uninstall script, Python 2.7 bindings, unloads/removes the LaunchDaemon plist, and removes package receipts.

## Control Flow
Performs destructive file removals first with shell tracing, then reports preserved data/config directories if data remains.

## State And Persistence Behavior
Deletes installed program files but intentionally preserves `/usr/local/foundationdb/data` and `/usr/local/etc/foundationdb` unless the user removes them manually.

## Dependencies And Integration Points
Depends on macOS filesystem layout and launchctl. Installed into `/usr/local/foundationdb` by the client package.

## Risks And Edge Cases
Brace expansion and broad receipt globbing assume bash and expected package IDs. Running as non-root may partially remove files. It does not remove `/usr/local/bin/backup_agent` if only symlink names listed omit it.

## Test Signals
Validated manually or by install/uninstall smoke tests checking no service remains and data preservation message appears.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/osx/uninstall-FoundationDB.sh -->
