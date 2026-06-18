# File Research: sources/local-fs/apfs-fuse/ApfsLib/DiskImageFile.cpp

`DiskImageFile` is a lower-level file wrapper for raw and encrypted Apple disk images. It opens an `ifstream`, detects encryption signatures, sets up decryption, and reads decrypted byte ranges.

`CheckSetupEncryption()` detects v1 encrypted DMGs by trailing `cdsaencr` and v2 by leading `encrcdsa`. V1 setup reads the trailing crypto header; V2 reads key pointer/key data records from the front of the image.

Both setup paths prompt for a password, derive a 3DES wrapping key with PBKDF2-HMAC-SHA1, unwrap AES and HMAC keys, and configure AES-CBC content decryption. Read-time IVs are derived as HMAC-SHA1 over the big-endian block number.

`Read()` handles unencrypted direct reads or encrypted block-aligned/unaligned reads through a temporary 0x1000 buffer and AES-CBC decryption with per-block IV.

Notable risks: password prompts are interactive, limiting automation. The encrypted read buffer is fixed at 0x1000, so images with larger crypto block sizes would overflow. HMAC/integrity verification is not performed; HMAC is only used for IV derivation.
