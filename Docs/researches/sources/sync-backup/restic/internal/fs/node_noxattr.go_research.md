# sources/sync-backup/restic/internal/fs/node_noxattr.go

Purpose: No-op xattr implementation for platforms without supported xattr handling in this package.

Important APIs: `nodeRestoreExtendedAttributes` and `nodeFillExtendedAttributes`.

Control flow and state: Both functions ignore inputs and return nil.

Dependencies and integration: Selected for AIX, DragonFly, and OpenBSD so generic node conversion/restoration can compile without xattr support.

Risks: Extended attributes are silently omitted on these platforms. This is intentional compatibility behavior but affects metadata fidelity.

Test signals: No direct tests; broader restore tests will see no xattrs on no-xattr platforms.
