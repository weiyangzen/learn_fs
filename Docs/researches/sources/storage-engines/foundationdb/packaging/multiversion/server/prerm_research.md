<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/multiversion/server/prerm -->
# Research: sources/storage-engines/foundationdb/packaging/multiversion/server/prerm

## Purpose
Pre-remove hook for multiversion server packages.

## Important APIs, Types, And Functions
Removes this versioned `fdbserver` from the alternatives group.

## Control Flow
Executed before package removal; alternatives may fall back to another installed server version.

## State And Persistence Behavior
Mutates alternatives database only.

## Dependencies And Integration Points
Depends on `update-alternatives` and correct version/build-time substitutions. Pairs with server postinstall alternatives registration.

## Risks And Edge Cases
Does not stop services itself; package manager ordering must ensure active service behavior is safe during removal or upgrade.

## Test Signals
Validated by multiversion remove/upgrade package tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/multiversion/server/prerm -->
