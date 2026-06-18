# sources/user-network-fs/libtirpc/tirpc/rpc/des_crypt.h

Purpose: `des_crypt.h` declares public DES encryption helpers for CBC and ECB modes plus key parity adjustment.

Important APIs, types, and functions: It defines `DES_MAXDATA`, mode flags `DES_ENCRYPT`, `DES_DECRYPT`, `DES_HW`, `DES_SW`, error codes, `DES_FAILED`, and functions `cbc_crypt`, `ecb_crypt`, and `des_setparity`.

Control flow: Callers combine direction and hardware/software flags, pass key, data, length, and optionally IV for CBC. Return codes distinguish full success, software fallback from missing hardware, and hard failures.

State and persistence behavior: The data buffer is modified in place. CBC IV is updated by the implementation. No global state is declared in the header.

Dependencies and integration points: It includes `rpc/rpc.h` and supports AUTH_DES/keyserv code paths.

Risks: DES is cryptographically deprecated. Length must be a multiple of eight and no more than `DES_MAXDATA`; callers must not assume hardware availability. In-place mutation can surprise callers that reuse plaintext buffers.

Test signals: Tests should cover encrypt/decrypt round trips, CBC IV mutation, ECB determinism, software fallback return handling, parity adjustment, and bad length/key inputs.
