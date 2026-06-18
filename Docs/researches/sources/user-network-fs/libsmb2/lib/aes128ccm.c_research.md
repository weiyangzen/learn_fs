# sources/user-network-fs/libsmb2/lib/aes128ccm.c

Purpose: Implements in-place AES-128 CCM authenticated encryption/decryption for SMB3 encryption/signing-related code paths. It builds the CCM authentication block stream from a caller-provided key, nonce, AAD, payload, and MAC buffer.

Important APIs/functions: `aes128ccm_encrypt` computes authentication tag `m`, masks it with counter block S0, then XOR-encrypts payload `p` in place. `aes128ccm_decrypt` decrypts payload in place first, recomputes the tag over plaintext, masks it, and returns `memcmp(tmp, m, mlen)`. Internal helpers include `aes_ccm_generate_b0`, `ccm_generate_T`, `ccm_generate_s`, `aes_ccm_crypt`, and `bxory`.

Control flow: Authentication starts with B0 flags containing AAD presence, tag length encoding, nonce length encoding, and 32-bit payload length. AAD is encoded with a 16-bit length prefix and CBC-MACed block by block. Payload blocks are CBC-MACed next. Counter-mode encryption uses generated S blocks with counter values starting at 1; S0 masks/unmasks the tag.

State/persistence: No global state. The payload and tag buffers are mutated in place. Stack buffers hold transient AES blocks. The API assumes `key`, `nonce`, `aad`, `p`, and `m` are valid for the supplied lengths.

Dependencies/integration: Includes `portable-endian.h`, `compat.h`, and `aes.h`; all block encryption goes through `AES128_ECB_encrypt`, which dispatches to Apple CommonCrypto or the reference implementation via `aes.c`. Tests reference it directly in `tests/aes128ccm-test.c`.

Risks: CCM parameter validation is minimal: nonce length, tag length, AAD length encoding, and payload length are trusted. The implementation stores payload length as 32-bit at bytes 12..15, so it is effectively limited to that CCM L=4 shape. `memcmp` is not constant-time, which can matter if authentication timing is observable. Decrypt mutates payload before authentication succeeds, so callers must discard plaintext on nonzero return.

Test signals: Run AES-CCM vectors in `tests/aes128ccm-test.c`, including encrypt/decrypt round trips and authentication failure. Boundary tests should cover empty AAD, empty payload, partial final blocks, bad tag, invalid nonce/tag lengths, and oversized lengths rejected at a higher layer.
