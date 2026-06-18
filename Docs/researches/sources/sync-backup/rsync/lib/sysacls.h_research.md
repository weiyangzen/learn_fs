# sources/sync-backup/rsync/lib/sysacls.h

## Purpose
`sysacls.h` defines rsync's portable ACL type vocabulary and function prototypes. It maps platform-native ACL tags, entry handles, ACL handles, and ACL type constants into `SMB_ACL_*` names originally inherited from Samba code, giving the rest of rsync a stable interface when `SUPPORT_ACLS` is enabled.

## Important APIs, Types, and Functions
The header conditionally defines `SMB_ACL_TAG_T`, `SMB_ACL_TYPE_T`, `SMB_ACL_T`, and `SMB_ACL_ENTRY_T`. It also defines common tag constants such as `SMB_ACL_USER`, `SMB_ACL_USER_OBJ`, `SMB_ACL_GROUP`, `SMB_ACL_GROUP_OBJ`, `SMB_ACL_OTHER`, and `SMB_ACL_MASK`, plus traversal constants `SMB_ACL_FIRST_ENTRY` and `SMB_ACL_NEXT_ENTRY`. Valid permission bit masks are expressed as `SMB_ACL_VALID_NAME_BITS` and `SMB_ACL_VALID_OBJ_BITS`. The prototypes exactly match the implementation surface in `sysacls.c`.

## Control Flow
There is no runtime flow; compile-time preprocessor branches select the correct platform layout. POSIX and Tru64 use native `acl_t` and `acl_entry_t`. Solaris/UnixWare and HPUX define an expandable struct containing `struct acl acl[1]`. IRIX wraps a native `struct acl *` plus traversal and ownership flags. AIX defines a linked-list entry model and a `new_acl_entry` wrapper around `ace_id`. macOS maps only user and group ACL identities and uses extended ACL constants.

## State and Persistence
The header has no persistent state. Its definitions determine ownership expectations for allocations returned by `sys_acl_get_file()` and `sys_acl_init()`, and the prototypes make `sys_acl_free_acl()` the required release path for all platform variants.

## Dependencies and Integration Points
The header includes system ACL headers when available and uses rsync allocation macros (`new_array`, `realloc_array`) through macro aliases such as `SMB_MALLOC`. It is included by `sysacls.c` and by higher-level ACL transfer code that needs the portable types and function declarations.

## Risks
Because the type definitions are selected entirely at compile time, a misdetected configure macro can produce incompatible ABI assumptions or the hard `#error` path. The AIX branch embeds assumptions about `/usr/include/acl.h` and specific internal structs. macOS exposes a different permission-bit domain from POSIX, so callers must honor the valid-bit masks.

## Test Signals
Compile tests on each supported ACL platform are essential because many branches cannot be covered on a single host. Header-level signals include successful builds with `SUPPORT_ACLS`, detection of `SMB_ACL_NEED_SORT` where expected, and unit or integration tests that compile callers against only this portable API rather than native ACL types.
