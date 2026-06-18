<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/pdbedit.c -->
# sources/user-network-fs/samba/source3/utils/pdbedit.c

## Purpose

`pdbedit.c` implements Samba's passdb editing command-line utility. It lists, creates, modifies, deletes, imports, exports, repairs, and policy-edits passdb user and machine accounts.

## Important APIs, Types, and Functions

The file is organized around command bitmasks such as `BIT_LIST`, `BIT_CREATE`, `BIT_MODIFY`, `BIT_DELETE`, `BIT_IMPORT`, and `BIT_ACCPOLICY`. Key functions are `print_sam_info()`, `print_user_info()`, `print_users_list()`, `fix_users_list()`, `set_user_info()`, `set_machine_info()`, `new_user()`, `new_machine()`, `delete_user_entry()`, `delete_machine_entry()`, `export_database()`, `export_groups()`, `export_account_policies()`, and `reinit_account_policies()`. `get_sid_from_cli_string()` accepts full SIDs or RIDs.

## Control Flow

`main()` initializes Samba cmdline and passdb state, parses options, builds `setparms`, optionally overrides the passdb backend via loadparm, initializes the password DB, then validates compatible option groups. Account-policy operations are handled early. Import/export constructs source and destination `pdb_methods` backends. Legacy-compatible cases promote a lone user argument into list mode and promote user field options into modify mode. Create, delete, and modify branches dispatch to user or machine variants.

## State and Persistence Behavior

This utility directly mutates passdb backends: it can add accounts, set passwords, update SIDs, update account flags, reset bad-password counters, reset logon hours, set kickoff time, set NT hashes and password history, delete users or machine accounts, migrate accounts/groups/policies, and reset policy defaults. Passwords read for new users are scrubbed before free. Backend override changes process loadparm state.

## Dependencies and Integration Points

It integrates with Samba passdb (`pdb_*`, `struct samu`, `pdb_methods`), SAMR display entries, account-policy helpers, local password change logic, cmdline/loadparm, SID utilities, and `get_pass()` from `passwd_util.c`.

## Risks and Edge Cases

The option compatibility mask is dense and easy to break when adding flags. Some error paths return without freeing temporary `samu` allocations, but process exit usually follows. Setting `--set-nt-hash` bypasses plaintext password policy and requires valid 32-hex-character input. Machine names are normalized to lowercase and `$`-suffixed, which can surprise callers. Import/export updates existing destination users by name, so a backend migration can overwrite attributes.

## Test Signals

Useful tests include list formats with verbose and smbpasswd-style output, create/delete/modify user and machine accounts, stdin password mismatch, SID-as-RID parsing, account-control validation, policy get/set/reset, import/export between temporary passdb backends, force-initialized password repair, and direct NT-hash setting with password-history verification.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/pdbedit.c -->
