# File Research: sources/os/bsd/freebsd-src/sys/fs/nfs/nfs_commonacl.c

## Purpose

`nfs_commonacl.c` converts between FreeBSD ACL entries and NFS wire encodings. It handles NFSv4 ACL ACE XDR parsing/building, POSIX draft ACL ACE XDR parsing/building, permission-mask translation, user/group string conversion, and ACL equality comparison.

## Main Entry Points

- `nfsrv_dissectace()` parses one NFSv4 ACE from an NFS descriptor into `struct acl_entry`.
- `nfsrv_dissectposixace()` parses one POSIX draft ACL ACE.
- `nfs_aceperm()` converts FreeBSD regular-file ACL permission bits to NFSv4 `acemask4`.
- `nfsrv_buildacl()` serializes a FreeBSD NFSv4 ACL as an NFSv4 ACL list.
- `nfsrv_buildposixacl()` serializes a POSIX draft ACL list.
- `nfsrv_compareacl()` compares two ACLs for same count, same tags, same ids for user/group entries, and same permissions for POSIX-style comparable entries.

Internal helpers include `nfsrv_acemasktoperm()`, `nfsrv_buildace()`, and `nfsrv_buildposixace()`.

## NFSv4 ACE Parsing

`nfsrv_dissectace()` reads ACE type, flags, mask, and who-string length from XDR. It bounds the who string to `NFSV4_OPAQUELIMIT`, treats zero-length who strings from NetApp filers as a deny ACE for `ACL_EVERYONE` with undefined id to avoid panics, and allocates temporary name storage only when the name exceeds `NFSV4_SMALLSTR`.

Special principals `OWNER@`, `GROUP@`, and `EVERYONE@` map to `ACL_USER_OBJ`, `ACL_GROUP_OBJ`, and `ACL_EVERYONE`. Other names map through `nfsv4_strtouid()` or `nfsv4_strtogid()` depending on `NFSV4ACE_IDENTIFIERGROUP`. Supported inheritance/audit flags are translated to FreeBSD ACL entry flags; unknown remaining flag bits produce `NFSERR_ATTRNOTSUPP`. Servers accept only allow/deny ACE types, while non-server parsing also accepts audit/alarm types. Permission masks are translated by `nfsrv_acemasktoperm()`.

## POSIX Draft ACE Parsing

`nfsrv_dissectposixace()` reads a numeric POSIX ACL tag, permission bits, and optional name. It validates the tag range, maps protocol tags through `nfsv4_to_posixacltag`, resolves ids only for `ACL_USER` and `ACL_GROUP`, and returns the ACE wire size when requested. Name lengths are bounded by `NFSV4_OPAQUELIMIT`.

## ACL Building

`nfsrv_buildacl()` emits an ACE count placeholder, iterates ACL entries, maps owner/group/everyone tags to special names, converts user/group ids to NFSv4 names with `nfsv4_uidtostr()` and `nfsv4_gidtostr()`, skips unsupported tags, serializes each ACE with `nfsrv_buildace()`, and finally writes the count. `nfsrv_buildace()` translates FreeBSD flags and type to NFSv4 ACE fields. Directory ACEs map directory-specific permissions such as list/add/search/delete-child explicitly, while non-directory ACEs use `nfs_aceperm()`.

`nfsrv_buildposixacl()` similarly emits POSIX draft ACL ACEs, using empty names for object/mask/other entries and id-to-string conversion only for named users and groups. A NULL ACL produces a zero entry count.

## Dependencies

This file depends on NFS XDR descriptor macros (`NFSM_DISSECT`, `NFSM_BUILD`, `nfsm_advance` through included infrastructure), mbuf string helpers (`nfsrv_mtostr()`), user/group mapping functions, ACL type/flag/permission constants, NFSv4 ACE constants, and NFS memory type `M_NFSSTRING`.

## Invariants And Risks

- Wire string lengths must be bounded before allocation or mbuf extraction.
- Unknown ACE flags, types, or mask bits must surface as `NFSERR_ATTRNOTSUPP` rather than being silently accepted.
- Directory and file ACE masks differ: directory search/list/add semantics are not identical to regular file read/write/execute semantics.
- Special principals must not be passed through id mapping.
- Build routines skip unsupported local ACL tags, so callers must understand that serialized ACE counts may be lower than local `acl_cnt`.
