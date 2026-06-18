# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zio_crypt.h

Defines ZIO encryption algorithm metadata, loaded-key representation, wrapping/unwrapping, IV/salt/MAC encoding helpers, indirect MAC checksums, HMAC helpers, and data/ABD encryption-decryption entry points.

Key elements:
- Constants define wrapping key/IV/MAC lengths, master key maximum, HMAC key length, and key format version.
- `zio_crypt_type_t` distinguishes none, CCM, and GCM.
- `zio_crypt_info_t` maps crypto mechanism name, mode type, key length, and human-readable name.
- `zio_crypt_key_t` stores encryption algorithm, version, GUID, master/HMAC/current key data, salt, salt use count, illumos crypto keys/templates, and salt lock.
- Prototypes cover key init/destroy, salt retrieval, key wrap/unwrap, IV generation, dedup IV/salt generation, block pointer parameter/MAC encode/decode, ZIL MAC encode/decode, dnode bonus copying, indirect MAC checksum, HMACs, objset HMACs, and data/ABD crypt.

Main dependencies and interactions:
- Depends on DMU, refcount, illumos crypto API, nvpair, AVL, and ZIO.
- Used by encrypted ZIO pipeline stages, raw send/receive metadata, and encrypted ZIL/objectset handling.

Implementation notes:
- Encryption routines expose both linear-buffer and ABD variants.
- Dedup encryption requires deterministic IV/salt generation from plaintext.
