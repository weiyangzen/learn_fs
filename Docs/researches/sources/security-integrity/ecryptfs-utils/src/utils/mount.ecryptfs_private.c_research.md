<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/mount.ecryptfs_private.c -->
# sources/security-integrity/ecryptfs-utils/src/utils/mount.ecryptfs_private.c

Final split target: `Docs/researches/sources/security-integrity/ecryptfs-utils/src/utils/mount.ecryptfs_private.c_research.md`. Source lines read for this pass: 716.

## Purpose
Setuid-capable private directory mount/unmount helper that lets non-root users mount configured eCryptfs private directories without fstab entries.

## Important APIs, Types, And Functions
Key helpers: `read_config`, `check_username`, `fetch_sig`, `check_ownership_mnt`, `check_ownerships`, `update_mtab`, `lock_counter`, `bump_counter`/`increment`/`decrement`/`zero`, and `main`.

## Control Flow
Drops effective uid to the caller, resolves default `Private` paths or alias `.conf`, locks a per-user counter in `/dev/shm`, validates username and signatures, builds fixed AES/16-byte mount options with FEK/FNEK signatures, chdirs into and canonicalizes the mountpoint, then either regains root to `mount()` or decrements session count, removes keys, and execs `/bin/umount -i -l .`.

## State And Persistence Behavior
Reads `~/.ecryptfs/<alias>.sig`, optional `<alias>.conf`, and `Private.mnt`; updates `/etc/mtab` when needed; maintains `/dev/shm/ecryptfs-$USER-$alias` session counters; changes keyring and mount state.

## Dependencies And Integration Points
Depends on setuid installation, keyutils, libecryptfs `ecryptfs_private_is_mounted` and key removal, mntent APIs, `/bin/umount`, and strict per-user ownership.

## Risks And Edge Cases
This is a high-risk privilege boundary. Ownership checks, username filtering, alias validation, counter locking, mtab updates, and retained real uid for keyring access are all security critical.

## Test Signals
Private setup scripts exercise normal paths. Additional tests should cover alias config rejection, invalid signatures, non-owned paths, concurrent sessions, forced unmount, mtab symlink behavior, and key cleanup.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/mount.ecryptfs_private.c -->
