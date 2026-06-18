## sources/user-network-fs/libtirpc/src/des_crypt.c

Purpose: Provides public DES encryption entry points `cbc_crypt` and `ecb_crypt` over libtirpc's software DES backend.

Important APIs and control flow: `cbc_crypt` sets `des_mode` to CBC, copies the IV into `desparams`, calls `common_crypt`, and copies the updated IV back. `ecb_crypt` uses ECB mode. `common_crypt` validates the buffer length is an 8-byte multiple and no larger than `DES_MAXDATA`, sets encrypt/decrypt direction from `DES_DIRMASK`, copies the 8-byte key, calls `_des_crypt`, and returns `DESERR_NONE` for requested software mode or `DESERR_NOHWDEVICE` when a hardware device was requested but software was used.

State and persistence: No persistent state. The caller's buffer and CBC IV are mutated in place.

Dependencies and integration: Uses `_des_crypt` from `des_impl.c` and DES constants/types from RPC headers. Export is conditional through map placeholders.

Risks and test signals: DES is legacy/weak cryptography. Tests should cover ECB/CBC known-answer vectors, invalid lengths, DES_HW fallback status, IV update semantics, and encrypt/decrypt round trips.
