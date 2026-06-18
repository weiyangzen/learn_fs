# File Research: sources/local-fs/apfs-fuse/ApfsLib/KeyMgmt.h

This header declares `Keybag` and `KeyManager`, the two public key-management classes for APFS encryption support. It includes `Global.h`, which in turn provides APFS disk structures and debug flags.

`Keybag` exposes initialization from a `media_keybag_t`, key count lookup, indexed key access, UUID/tag key search, and formatted dumping. It owns the copied keybag bytes and a pointer to the locker structure inside that vector.

`KeyManager` exposes initialization from a keybag block range and container UUID, password hint retrieval, volume key derivation, validity/unencrypted status, and dumping. Private helpers load/decrypt keybags and decode DER KEK/VEK records.

The class is bound to an `ApfsContainer&`, so key operations read blocks through the container abstraction and use the container block size. The `GetVolumeKey()` declaration allows `password = nullptr`, but the implementation requires a valid C string when it reaches PBKDF2.
