# sources/user-network-fs/nfs-utils/support/export/v4root.c

## Purpose
Synthesizes NFSv4 pseudo-root exports for parent directories so NFSv4 clients can traverse to real exported paths even when those parents are not explicitly exported.

## Important APIs, Types, and Functions
Important functions include `v4root_set()`, `v4root_add_parents()`, `pseudofs_update()`, `v4root_create()`, `v4root_support()`, and `set_pseudofs_security()`. It uses a static `pseudo_root` template export.

## Control Flow
`v4root_set()` exits unless pseudo roots are needed and kernel features advertise `NFSEXP_V4ROOT`. It walks all exports, forces `/` to fsid 0 when needed, and creates or updates pseudo exports for each path prefix. Non-root pseudo exports may get deterministic UUIDs from a fixed seed when kernel export testing without fsid fails.

## State and Persistence Behavior
Creates new entries in the global export list through `export_create()`. `v4root_needed` is set by etab reads. Pseudo exports are in-memory until normal etab/cache write paths persist or communicate them.

## Dependencies and Integration Points
Depends on `exportfs.h`, `nfslib.h`, `misc.h`, `v4root.h`, `pseudoflavors.h`, libuuid, kernel export feature probing, and `/etc/krb5.keytab` presence for security flavor filtering.

## Risks and Edge Cases
Error handling is limited in the main walk. Security flavor choices depend on local keytab existence. Deterministic UUID generation strips hyphens and relies on fixed seed behavior. Existing non-V4ROOT exports block pseudo replacement.

## Test Signals
Test kernel feature absent/present, export of `/` without fsid, nested path parent creation, existing pseudo update, krb5 keytab gating, export_test failure UUID generation, and repeated `v4root_set()` idempotence.
