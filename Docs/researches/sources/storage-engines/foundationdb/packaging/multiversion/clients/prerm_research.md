<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/multiversion/clients/prerm -->
# Research: sources/storage-engines/foundationdb/packaging/multiversion/clients/prerm

## Purpose
Pre-remove hook for multiversion client packages.

## Important APIs, Types, And Functions
Runs `update-alternatives --remove fdbclients` for this versioned `fdbcli` path.

## Control Flow
Executed before package removal to detach this version from the alternatives group.

## State And Persistence Behavior
Mutates Debian alternatives database and may switch public links to another installed version.

## Dependencies And Integration Points
Depends on `update-alternatives` and the same version/build-time substitution path used at install. Complements the multiversion client postinstall hook.

## Risks And Edge Cases
If the installed path template changes, removal can fail to remove the old alternative. No explicit error handling is present.

## Test Signals
Validated by install/remove alternatives tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/multiversion/clients/prerm -->
