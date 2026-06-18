# File Research: sources/os/linux/linux/fs/crypto/keyring.c

## Summary
Implements fscrypt filesystem-level master-key management and the related ioctls. It stores master keys per superblock, tracks which users added v2 keys, supports provisioning keys from the Linux keyrings service, handles hardware-wrapped key setup, supports test dummy encryption, removes keys safely, evicts decrypted inodes when possible, and reports key status.

## Main Responsibilities
- Maintain `sb->s_master_keys`, a per-filesystem hash table of `fscrypt_master_key` objects.
- Manage active and structural references for master-key lifecycle.
- Register and use internal key types `.fscrypt` and `fscrypt-provisioning`.
- Add master keys via `FS_IOC_ADD_ENCRYPTION_KEY`.
- Remove current-user or all-user key claims via remove-key ioctls.
- Track v2 key ownership per user using an internal keyring under each master key.
- Derive key identifiers with HKDF, including distinct raw-key and hardware-wrapped-key contexts.
- Retrieve keys from `fscrypt-provisioning` Linux keyring entries.
- Add and identify per-boot random test dummy keys.
- Evict dentries/inodes unlocked with a removed key and report busy files.
- Report present, absent, or incompletely removed key state.

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
Master keys can be present, incompletely removed, or absent. Removing a present key wipes its secret and drops the active ref associated with `mk_present`. If decrypted inodes still reference it, the object remains in the filesystem keyring in an incompletely removed state until those inodes are evicted or the key is re-added.

V2 policy keys are identified by cryptographic identifiers rather than arbitrary descriptors. Each user adding a v2 key gets a user-specific internal key under `mk_users`; a user cannot remove the key itself while other users still have claims unless using the privileged all-users ioctl.

Adding a hardware-wrapped key derives a software secret through inline-encryption hardware, initializes HKDF from that software secret, and uses a separate HKDF context for the key identifier to keep raw and wrapped-key identifiers distinct.

Removal first clears user claims, then initiates key removal if no claims remain. It syncs the filesystem, prunes dentries for decrypted inodes, relies on `fscrypt_drop_inode()` to evict inodes when refs drop, and reports `FILES_BUSY` if inodes remain.

## Research Notes
This file is the fscrypt key lifecycle authority. Correctness depends on `mk_sem`, `s_master_keys->lock`, RCU lookup, active/struct refcount transitions, keyring quota behavior, and cooperation with inode teardown in `keysetup.c`.
