# File Research: sources/os/linux/linux-stable/fs/crypto/keyring.c

## Summary
Implements fscrypt filesystem-level master-key management and the related ioctls. It maintains per-superblock master keys, tracks users that added v2 keys, provisions keys from a dedicated Linux key type, supports hardware-wrapped keys and test dummy encryption, removes keys safely, evicts decrypted inodes when possible, and reports key status.

## Main Responsibilities
- Maintain `sb->s_master_keys`, a per-filesystem hash table of `fscrypt_master_key` objects.
- Manage active and structural references for master-key lifecycle.
- Register internal key types `.fscrypt` and `fscrypt-provisioning`.
- Add master keys through `FS_IOC_ADD_ENCRYPTION_KEY`.
- Remove current-user or all-user key claims through remove-key ioctls.
- Track v2 key ownership per user using a keyring under each master key.
- Derive v2 key identifiers with HKDF, using distinct contexts for raw and hardware-wrapped keys.
- Retrieve provisioning keys from Linux keyring entries.
- Generate and add per-boot random test dummy encryption keys.
- Evict dentries/inodes unlocked by removed keys and report busy files.
- Return absent, present, or incompletely removed key status.

## Key APIs
- `fscrypt_find_master_key()`
- `fscrypt_put_master_key()`
- `fscrypt_put_master_key_activeref()`
- `fscrypt_ioctl_add_key()`
- `fscrypt_ioctl_remove_key()`
- `fscrypt_ioctl_remove_key_all_users()`
- `fscrypt_ioctl_get_key_status()`
- `fscrypt_get_test_dummy_key_identifier()`
- `fscrypt_add_test_dummy_key()`
- `fscrypt_verify_key_added()`
- `fscrypt_init_keyring()`
- `fscrypt_destroy_keyring()`

## Important Behavior
Master keys can be present, incompletely removed, or absent. Removing a present key clears `mk_present`, wipes the secret, and drops the active ref associated with presence. If decrypted inodes still reference it, the object stays in the filesystem keyring in the incompletely removed state until those inodes are evicted or the key is re-added.

V2 policy keys are identified by cryptographic identifiers rather than arbitrary descriptors. Each user adding a v2 key gets a user-specific claim under `mk_users`; a normal remove ioctl removes only the current user's claim and removes the key itself only when no claims remain. The all-users ioctl requires `CAP_SYS_ADMIN`.

Hardware-wrapped key addition asks inline-crypto hardware for a software secret, initializes HKDF from that software secret, and derives the public key identifier using a hardware-wrapped-specific HKDF context. This prevents a raw key equal to a derived software secret from colliding with a wrapped key identifier.

Removal syncs the filesystem, prunes dentries for decrypted inodes, relies on `fscrypt_drop_inode()` to evict inodes once references drop, and reports `FILES_BUSY` when inodes remain. It returns success for useful progress while placing final state details in status flags.

## Research Notes
This file is the fscrypt key lifecycle authority. Correctness depends on `mk_sem`, the `s_master_keys` spinlock, RCU lookup, acquire/release publication of the filesystem keyring, active/structural ref transitions, keyring quota behavior, and cooperation with inode teardown in `keysetup.c`.
