# sources/user-network-fs/samba/source3/utils/smbcacls.c

`smbcacls.c` implements remote SMB file security descriptor inspection and mutation. It supports Samba text ACL syntax, SDDL, owner/group changes, inheritance changes, maximum-access queries, recursive DACL save, and restore from icacls-compatible UTF-16 path/SDDL files.

Important functions include `sec_desc_parse`, `get_secdesc_with_ctx`, `set_secdesc`, `get_fileinfo`, `cacl_dump`, `cacl_set`, `cacl_set_from_sd`, `owner_set`, `inherit`, and `cacl_mxac`. Inheritance propagation is handled by `prepare_inheritance_propagation`, `get_inheritable_aces`, `get_flags_to_propagate`, `propagate_inherited_aces`, `cacl_set_cb`, and `inheritance_cacl_set`. Save/restore is handled by `write_dacl`, directory traversal callbacks, `cacl_dump_dacl`, and `cacl_restore`.

`main` parses options, validates `//server/share filename`, connects with Samba credentials, resolves DFS paths, and dispatches based on requested action. Mutations open files with access masks derived from selected security-info bits, query or construct descriptors, canonicalize ACE ordering, and call `cli_set_security_descriptor`.

Persistent state is remote file security metadata plus optional local save files. Dependencies include Samba client APIs, LSA RPC for SID/name/domain lookup, SDDL/security helpers, DFS resolution, local UTF-16 conversion, and command-line credentials. Risks include privilege-sensitive SACL handling, complex recursive inheritance mutation, callback error propagation through `cli_list`, restore file assumptions, and limited validation in `--test-args`. Test signals: ACL/SDDL parse errors, set/add/delete/modify, owner/group, inheritance modes, propagation, DFS, max access, save/restore round trips, and security-info masks.
