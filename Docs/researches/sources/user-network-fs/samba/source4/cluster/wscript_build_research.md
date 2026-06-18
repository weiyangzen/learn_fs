# sources/user-network-fs/samba/source4/cluster/wscript_build

## Purpose
Build definition for the source4 private `cluster` library.

## Important APIs, types, and functions
Declares `bld.SAMBA_LIBRARY('cluster', source='cluster.c local.c', deps='dbwrap samba-hostconfig talloc', private_library=True)`.

## Control flow
No runtime flow. Waf reads this file during configuration/build to include the cluster dispatch and local backend objects.

## State and persistence behavior
No runtime state. Build output is a private Samba library, not a public installed library.

## Dependencies and integration points
Links the library against `dbwrap`, `samba-hostconfig`, and `talloc`. The dependency set matches `local_db_tmp_open()` and backend initialization needs.

## Risks and edge cases
Any future cluster backend source added under this directory will not be built unless this file is updated. Since the library is private, external consumers should not depend on it.

## Test signals
Build-system validation should confirm the `cluster` private library is produced and linked into consumers needing cluster APIs.
