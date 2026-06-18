# sources/user-network-fs/nfs-ganesha/src/Protocols/XDR/xdr_nfsacl.c

Purpose: implements XDR routines for the NFSACL v3 extension: attribute wrapper, POSIX ACL entries, ACL vectors, getacl arguments/results, and setacl arguments/results.

Important APIs and types: `xdr_attr3()`, `xdr_posix_acl_entry()`, `xdr_posix_acl()`, `xdr_getaclargs()`, `xdr_getaclresok()`, `xdr_getaclres()`, `xdr_setaclargs()`, `xdr_setaclresok()`, `xdr_setaclres()`, `posix_acl`, `posix_acl_entry`, `getaclargs`, `getaclres`, and `setaclargs`.

Control flow: `xdr_attr3()` serializes a boolean and optional NFSv3 attributes. `xdr_posix_acl()` reads/writes a count, rejects counts over 4096, then serializes exactly that many fixed entries with `xdr_vector()`. Get/set result routines switch on `NFS3_OK` and only serialize success payloads for success. ACL pointer handling uses `xdr_reference()` when memory is already supplied or on decode paths that need allocated storage, and `xdr_pointer()` when nullable semantics are desired.

State and persistence: no persistent state. Decode/free may allocate and free ACL buffers sized as `sizeof(posix_acl) + count * sizeof(posix_acl_entry)`.

Dependencies and integration points: depends on NFSv3 XDR helpers from `xdr_nfs23.c` and ACL protocol definitions in `nfsacl.h`. This bridges NFSACL protocol dispatch to FSAL ACL handling elsewhere.

Risks: count-derived allocation sizes can become large even with the 4096 cap; callers must ensure decoded ACL counts match allocated entry arrays. `xdr_vector()` expects contiguous entries, so structure layout must match the protocol definition. Setacl decode forces allocation even if counts are zero, so free paths should be covered.

Test signals: getacl/setacl success and error round trips, null and non-null ACL pointers, zero ACL counts, maximum allowed count, count above 4096 rejection, and XDR_FREE on decoded ACLs.
