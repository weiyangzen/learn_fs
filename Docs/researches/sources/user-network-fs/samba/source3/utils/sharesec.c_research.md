# sources/user-network-fs/samba/source3/utils/sharesec.c

`sharesec.c` implements the `sharesec` utility for viewing and modifying Samba share security descriptors. It supports add/modify/remove/replace ACL text operations, full SDDL set/view, deleting descriptors, viewing every share, and machine SID initialization.

Core functions are `parse_acl_string`, `add_ace`, `sort_acl`, `change_share_sec`, `set_sharesec_sddl`, `view_sharesec_sddl`, and share-existence helpers for registry and text smbconf backends. `change_share_sec` loads the current descriptor except for replace/delete modes, parses requested ACEs, applies add/delete/modify/set/view behavior, canonicalizes and deduplicates the DACL, and persists through `set_share_security`.

`main` initializes Samba command-line state, parses popt options, loads configuration with or without registry shares depending on mode, handles machine SID output, validates share existence, and dispatches to ACL or SDDL handling. Persistent state is the share security descriptor managed by Samba share-security helpers; `--delete` removes it.

Dependencies include loadparm, smbconf, machine SID helpers, security descriptor utilities, SDDL encode/decode, and `util_sd.h`. Risks include limited comma-separated ACL parsing, an apparently ineffective `--force` except for rejecting view+force, and normal backend differences between registry and file-configured shares. Test signals: all modes, duplicate ACE sorting, invalid ACL/SDDL, registry/text share validation, view-all output, descriptor deletion, and SDDL round trips.
