<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/profiles.c -->
# sources/user-network-fs/samba/source3/utils/profiles.c

## Purpose

`profiles.c` rewrites a Windows registry hive/profile file into a new `.new` file, optionally replacing one SID with another inside registry security descriptors. It is used for profile migration or ownership remapping.

## Important APIs, Types, and Functions

Global `old_sid`, `new_sid`, `change`, `new_val`, and `opt_verbose` hold command state. `verbose_output()` conditionally prints details. `swap_sid_in_acl()` replaces matching owner, group, and DACL trustee SIDs in a `security_descriptor`. `copy_registry_tree()` recursively copies keys, values, subkeys, and security descriptors from one `REGF_FILE` to another.

## Control Flow

`main()` parses `--change-sid`, `--new-sid`, and `--verbose`, requires both SID options if either is supplied, opens the original profile read-only, creates `<profilefile>.new`, fetches the root key, and calls `copy_registry_tree()`. The recursive copy duplicates the source security descriptor, performs SID replacement, collects values into a `regval_ctr`, collects subkey names into a `regsubkey_ctr`, writes the key into the output file, then recurses into each fetched subkey.

## State and Persistence Behavior

The original hive is read-only. The output hive is created with owner read/write permissions and truncated if already present. SID replacement only affects copied security descriptors in the new file. Values and subkey structure are preserved, with value data sizes masked by `~VK_DATA_IN_OFFSET`.

## Dependencies and Integration Points

It depends on Samba registry file I/O (`regfio`), registry object containers, security descriptor/SID utilities, filesystem flags, and Samba cmdline initialization. It does not use the live Samba registry service.

## Risks and Edge Cases

`swap_sid_in_acl()` assumes `sd->owner_sid`, `sd->group_sid`, and `sd->dacl` are non-NULL; malformed descriptors can crash despite a top-level `sec_desc` NULL check. SACL rewrite is disabled. The code always calls `swap_sid_in_acl()` even when SID options were not supplied, relying on zero-initialized globals. Output naming is fixed to `.new` and may overwrite an existing file.

## Test Signals

Tests should use small REGF fixtures with owner/group/DACL SID matches, no matches, nested keys, values with inline data, NULL or missing ACL components, missing root keys, and invalid SID command arguments. A binary comparison of key/value structure plus descriptor SID changes is the main validation signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/profiles.c -->
