<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/enablerecyclebin -->
# sources/user-network-fs/samba/source4/scripting/bin/enablerecyclebin

## Purpose

`enablerecyclebin` enables the Active Directory Recycle Bin optional feature on a target Samba LDB URL.

## Important APIs, Types, and Functions

It uses `optparse`, Samba option/credential helpers, `samba.Ldb`, `system_session()`, rootDSE search, and an `ldb.Message` modification of `enableOptionalFeature`.

## Control Flow

The script requires one URL argument, loads smb.conf and credentials, opens the LDB with system session, searches rootDSE for `configurationNamingContext`, constructs a modify message on the root DN, and adds the Recycle Bin feature identifier under `CN=Partitions`.

## State and Persistence Behavior

It persists an AD configuration change by modifying `enableOptionalFeature`. The change is domain/forest significant and not local script state.

## Dependencies and Integration Points

It integrates Samba Python bindings, LDB, credentials, and AD optional-feature semantics.

## Risks and Edge Cases

It does not prompt for confirmation or check whether the feature is already enabled. Failures are mostly raw exceptions. Correct privileges are required, and enabling Recycle Bin is not a trivial reversible operation.

## Test Signals

Tests should use a disposable provision, verify rootDSE discovery, insufficient-privilege failure, idempotent/already-enabled behavior, and post-change feature visibility.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/enablerecyclebin -->
