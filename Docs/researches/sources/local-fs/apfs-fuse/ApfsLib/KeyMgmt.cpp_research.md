# File Research: sources/local-fs/apfs-fuse/ApfsLib/KeyMgmt.cpp

This file implements APFS keybag handling and password-based volume-key recovery for encrypted volumes. It depends on `ApfsContainer`, ASN.1 DER parsing, AES-XTS, SHA-256/HMAC/PBKDF2/RFC3394 key unwrap helpers, utility formatting/logging, and disk structures from `DiskStruct.h`.

`Keybag` owns a copied keybag locker blob. `Init()` accepts a `media_keybag_t`, requires locker version 2, copies `kl_nbytes` from the locker, and stores `m_kl` as a pointer into the owned vector. `GetKeyCnt()` reports `kl_nkeys`. `GetKey()` walks aligned `keybag_entry_t` records by rounding each entry size to 16-byte alignment. `FindKey()` scans entries for matching UUID and tag.

`Keybag::dump()` prints keybag metadata and each key record. For container keybags it labels volume keys and keybag references; for volume unlock-record bags it labels KEKs and password hints. It can DER-dump key blobs, print keybag reference block ranges, and optionally dump raw key material if `DUMP_RAW_KEYS` is enabled. The debug output explicitly warns that password-derived keys, KEKs, and VEKs are sensitive.

`KeyManager` owns a reference to the container, the loaded container keybag, the container UUID, and validity/unencrypted flags. `Init()` loads the container keybag from a block range and records validity. `GetPasswordHint()` locates a volume unlock-record pointer in the container keybag, loads the volume records keybag, then extracts `KB_TAG_VOLUME_PASSPHRASE_HINT`.

`GetVolumeKey()` is the main encrypted-volume path. It loads the volume records keybag referenced by the container keybag, iterates all KEK entries, DER-decodes each KEK, derives a 256-bit password key using `PBKDF2_HMAC_SHA256(password, salt, iterations)`, and tries RFC3394 unwrapping. If the KEK blob flags indicate the AES-128 wrapping variant, it unwraps 16 bytes and records AES-128 mode; otherwise it unwraps 32 bytes using AES-256. Once a KEK works, it finds the container VEK entry, DER-decodes it, and unwraps the VEK. For the AES-128/FileVault/CoreStorage-converted variant, it derives the second half of the XTS key by hashing `(VEK || vek_blob.uuid)` and taking 16 bytes; otherwise it unwraps the full 32-byte XTS key.

`LoadKeybag()` reads a keybag block range from the APFS container. If the object type is already the expected keybag type, it marks the key manager as unencrypted. Otherwise it decrypts the blocks using AES-XTS with the supplied UUID as both halves of the key, then verifies block checksums and initializes a `Keybag`. This supports APFS keybag storage where keybag blocks may be encrypted at rest.

`DecryptBlocks()` decrypts a block range in 512-byte units with AES-XTS. The tweak starts at `block * (container_block_size / 512)` and increments per 512-byte sector. This matches APFS’s sector-based XTS treatment inside larger filesystem blocks.

The DER decoding helpers parse APFS key headers, verify an HMAC-SHA256 over the DER body using a key derived from a fixed cookie and salt, then decode KEK- or VEK-specific fields. HMAC failure is logged but currently ignored, allowing parsing to proceed.

Notable risks and limitations: `LoadKeybag()` loops over `blockcnt` but calls `VerifyBlock(data.data(), blockcnt * blocksize)` each time, so the loop index is unused and it verifies the whole buffer repeatedly rather than each block. `Keybag::Init()` has a TODO noting it only works with one block. The DER HMAC check logs but does not reject invalid HMACs. `GetVolumeKey()` defaults `password` to `nullptr` in the header but passes it to `strlen(password)`, so callers must not rely on the default for encrypted volumes.
