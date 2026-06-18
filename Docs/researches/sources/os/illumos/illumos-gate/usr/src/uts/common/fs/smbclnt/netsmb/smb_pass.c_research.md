# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb_pass.c

## Purpose
Implements an in-kernel SMB password-hash keychain using an AVL tree keyed by local UID, zone ID, SMB domain/server name, and SMB username.

## Key Elements
The global `smb_ptd` AVL tree stores `smb_passid_t` nodes containing owner UID, zone, server/domain string, username string, LM hash, and NT hash. `smb_pkey_cmp` orders entries by UID, zone, server/domain, then username, with case-insensitive Unicode comparison for strings. `smb_pkey_init`, `smb_pkey_fini`, and `smb_pkey_idle` initialize/destroy the tree and prevent driver unload while hashes remain stored.

`smb_pkey_add` resolves `pk_uid` of `-1` to the caller's real UID or checks privilege for another UID, duplicates the domain/user strings, copies supplied hashes, deletes any existing matching entry, and inserts the new node. `smb_pkey_del` removes a single matching entry. `smb_pkey_deluid` removes all entries for a UID, or all entries when passed `(uid_t)-1`, after a policy check. `smb_pkey_check` looks up an entry and copies only LM/NT hashes back into the ioctl structure.

`smb_pkey_ioctl` dispatches `SMBIOC_PK_ADD`, `SMBIOC_PK_DEL`, `SMBIOC_PK_CHK`, `SMBIOC_PK_DEL_OWNER`, and `SMBIOC_PK_DEL_EVERYONE`, performing copyin/copyout and ensuring string buffers are nul-terminated before use.

## Dependencies
Depends on illumos AVL APIs, kernel memory allocation, credentials and `secpolicy_smbfs_login`, zones, UTF-8 comparison, SMB ioctl structures from `smb_dev.h`, and string allocation helpers.

## Behavior/Risks
Stored credentials are hashes rather than plaintext passwords, but they remain sensitive kernel memory and are intentionally never copied to userland except through the hash-check ioctl path. The tree is zone-scoped as part of the key to avoid cross-zone credential reuse. `smb_pkey_add` has a noted race-prone pattern where it checks and deletes outside one AVL critical section; current locking still protects tree operations individually, but changing this path should make lookup/remove/insert atomic. Unload depends on the tree being empty.
