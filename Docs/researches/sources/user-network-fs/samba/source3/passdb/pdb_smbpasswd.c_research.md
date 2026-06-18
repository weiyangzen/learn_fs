# sources/user-network-fs/samba/source3/passdb/pdb_smbpasswd.c

## Purpose
`pdb_smbpasswd.c` implements the legacy flat-file `smbpasswd` passdb backend. It stores a limited subset of `struct samu` as colon-separated lines containing username, Unix uid, LM hash, NT hash, account-control flags, and password-last-set time. The backend is compatibility-focused and depends on local Unix passwd entries and algorithmic RID-to-uid mappings.

## Important APIs, Types, And Functions
`struct smb_passwd` is the on-disk record model: Unix uid, username, LM/NT hashes, account-control bits, and password last-set time. `struct smbpasswd_privates` stores per-backend runtime state: recursive lock depth, an optional file pointer, parse buffers, hash buffers, and the configured smbpasswd file path.

File access is managed by `do_file_lock()`, `pw_file_lock()`, `pw_file_unlock()`, `startsmbfilepwent()`, and `endsmbfilepwent()`. `startsmbfilepwent()` handles read/update/create modes, `fcntl()` locks with timeout, atomic creation, rename-race detection via stat/fstat inode comparison, buffering, and permission repair to `0600`.

Parsing and formatting are done by `getsmbfilepwent()` and `format_new_smbpasswd_entry()`. Mutation helpers are `add_smbfilepwd_entry()`, `mod_smbfilepwd_entry()`, and `del_smbfilepwd_entry()`. Conversion between legacy records and passdb records is done by `build_smb_pass()` and `build_sam_account()`.

The passdb method implementations are `smbpasswd_getsampwnam()`, `smbpasswd_getsampwsid()`, `smbpasswd_add_sam_account()`, `smbpasswd_update_sam_account()`, `smbpasswd_delete_sam_account()`, `smbpasswd_rename_sam_account()`, `smbpasswd_search_users()`, and `smbpasswd_capabilities()`. `pdb_init_smbpasswd()` builds the method table and private state, while `pdb_smbpasswd_init()` registers the backend name `smbpasswd`.

## Control Flow
Reads open the smbpasswd file with a read lock and iterate line by line. `getsmbfilepwent()` skips comments and blank lines, parses `username:uid:lmhash:nthash:[acct flags]:LCT-XXXXXXXX:` formats, tolerates old records without NT hashes or account-control fields, marks invalidated hashes as null, and infers workstation trust accounts for old-style names ending in `$`. `smbpasswd_getsampwnam()` stops when the username matches; `smbpasswd_getsampwsid()` converts the requested RID to an algorithmic uid, except for the guest RID which maps through `lp_guest_account()`.

Adding a user opens the file for update, creates it if needed, scans for duplicate names, seeks to EOF, formats a complete new line, writes with raw `write()`, and truncates back to the old EOF on short write failure. Updating an existing user opens with a write lock, finds the target line, validates the fixed-width hash and flag/time fields, builds replacement text of exactly the supported field span, sanity-checks surrounding colons, and overwrites in place. Deleting rewrites every non-target record to a per-process temporary file and then renames the temporary file over the original.

`build_smb_pass()` rejects users whose RID cannot be represented as a Unix uid-based algorithmic RID, except the guest RID which maps to the configured guest Unix account. `build_sam_account()` performs the reverse conversion by looking up the Unix account with `Get_Pwnam_alloc()`, using `samu_set_unix()`, and setting hashes, flags, and password timestamps.

Rename is a two-phase compatibility operation. It creates an interim new smbpasswd entry, runs the configured `rename user script` with `%unew` and `%uold` substitutions, flushes nscd on success, deletes the old account, and rolls back the interim new entry if the script path fails.

Search materializes all matching users into a `smbpasswd_search_state` array of `samr_displayentry` values by parsing file records, converting each to `struct samu`, filtering account-control bits, and exposing results through `next_entry`/`search_end`.

## State And Persistence
Persistent state is the configured smbpasswd flat file, defaulting to `lp_smb_passwd_file()` unless a module location is supplied. The file is chmodded to owner read/write only. Adds and updates mutate this file in place under locks; deletes replace it by rename from a temporary file named with the current pid.

Runtime state is the private lock depth, parse buffers, reusable `struct smb_passwd`, and configured path. Because parsing returns pointers into reusable buffers, callers must consume each parsed record before the next `getsmbfilepwent()` call. The backend advertises no special capabilities; it does not store arbitrary RIDs or full AD/passdb metadata.

## Dependencies And Integration Points
The backend depends on source3 passdb APIs, Unix passwd APIs, filesystem/stat/lock functions, generated SAMR definitions, SID helpers, account-control encode/decode helpers, hash hex helpers, loadparm (`lp_smb_passwd_file()`, `lp_guest_account()`, `lp_rename_user_script()`), algorithmic RID helpers, `samu_set_unix()`, `smbrun()`, and nscd cache flushing.

It integrates as a passdb module through `smb_register_passdb(PASSDB_INTERFACE_VERSION, "smbpasswd", pdb_init_smbpasswd)`. It is mainly relevant for legacy local-file installations and migration compatibility.

## Risks
This backend stores only a small subset of passdb state. Full names, descriptions, group mappings, policies, trust data, password history, and many AD attributes cannot round-trip through this file. It depends on local Unix accounts existing for every smbpasswd entry; stale Unix passwd data makes the passdb record unusable.

The file format is fixed-width and update-in-place; malformed lines, long usernames, unsupported old formats, or unexpected field lengths can prevent updates. Locking uses process alarms and whole-file byte-range locks, so interactions with other tools that ignore locking can corrupt data. Delete-by-rewrite renames a temporary file over the original while locks are held on both streams, but failures after rename are only logged. Rename can leave Unix and smbpasswd state inconsistent if the external script succeeds but later deletion fails, or if multiple tools mutate the file concurrently.

There is a notable logic issue in `smbpasswd_getsampwsid()`: `nt_status` is initialized to unsuccessful and never set to OK before the post-build SID equality check, so the intended mismatch check is skipped. The function still returns OK after successful build, but that guard is ineffective.

## Test Signals
Tests should cover parsing old and new record formats, invalid hashes, disabled/no-password markers, trust-account inference, comments and long lines, missing Unix passwd entries, guest SID mapping, algorithmic RID conversion, add duplicate rejection, add rollback on short write, update of hashes/flags/LCT, rejection of old unsupported update format, delete rewrite and permissions, lock timeout behavior, rename-script success/failure rollback, and search filtering by account flags.

Regression tests should explicitly exercise lookup by SID and confirm the returned `struct samu` SID matches the requested SID, catching the currently ineffective mismatch guard. Integration tests should verify behavior with `lp_smb_passwd_file()` and with an explicit module location.
