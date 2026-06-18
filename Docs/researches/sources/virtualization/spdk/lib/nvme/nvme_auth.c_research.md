# File Research: sources/virtualization/spdk/lib/nvme/nvme_auth.c

## Purpose

`nvme_auth.c` implements NVMe-oF DH-HMAC-CHAP authentication for SPDK NVMe qpairs. It provides digest and Diffie-Hellman group lookup APIs, DH-HMAC-CHAP key transformation and response calculation, OpenSSL-backed DH key generation/secret derivation, and the qpair authentication state machine used for fabrics connections.

Most functional code is compiled only when `SPDK_CONFIG_HAVE_EVP_MAC` is enabled. The digest/group name lookup helpers are always present.

## Main Responsibilities

- Defines supported DH-HMAC-CHAP hash digests:
  - SHA-256
  - SHA-384
  - SHA-512

- Defines supported DH groups:
  - `null`
  - `ffdhe2048`
  - `ffdhe3072`
  - `ffdhe4096`
  - `ffdhe6144`
  - `ffdhe8192`

- Exposes digest/group mapping helpers:
  - `spdk_nvme_dhchap_get_digest_id()`
  - `spdk_nvme_dhchap_get_digest_name()`
  - `spdk_nvme_dhchap_get_dhgroup_id()`
  - `spdk_nvme_dhchap_get_dhgroup_name()`
  - `spdk_nvme_dhchap_get_digest_length()`

- Implements DH-HMAC-CHAP cryptographic helpers:
  - Parse DHHC-1 formatted CHAP keys from SPDK key objects.
  - Validate key size and CRC32 checksum.
  - Transform keys according to DH-HMAC-CHAP hash/NQN rules.
  - Generate host DH public keys.
  - Derive DH shared secrets from peer public keys.
  - Calculate CHAP response values with HMAC.

- Implements fabrics qpair authentication:
  - `nvme_fabric_qpair_authenticate_async()`
  - `nvme_fabric_qpair_authenticate_poll()`
  - `spdk_nvme_qpair_authenticate()`

## Authentication State Machine

The state machine is stored in `qpair->auth.state` and driven by `nvme_fabric_qpair_authenticate_poll()`:

1. `NVME_QPAIR_AUTH_STATE_NEGOTIATE`
   - Sends `AUTH_negotiate` with allowed digest and DH group lists.
   - Moves to `AWAIT_NEGOTIATE`.

2. `NVME_QPAIR_AUTH_STATE_AWAIT_NEGOTIATE`
   - Waits for Authentication Send completion.
   - Issues Authentication Receive for challenge.
   - Moves to `AWAIT_CHALLENGE`.

3. `NVME_QPAIR_AUTH_STATE_AWAIT_CHALLENGE`
   - Waits for challenge receive completion.
   - Validates message type, transaction ID, sequence number, hash length, DH group, DH value length, and policy allow-lists.
   - Sends DH-HMAC-CHAP reply.
   - Moves to `AWAIT_REPLY`.

4. `NVME_QPAIR_AUTH_STATE_AWAIT_REPLY`
   - Waits for reply send completion.
   - Issues receive for `success1`.
   - Moves to `AWAIT_SUCCESS1`.

5. `NVME_QPAIR_AUTH_STATE_AWAIT_SUCCESS1`
   - Validates controller success response.
   - If bidirectional authentication is enabled with `dhchap_ctrlr_key`, sends `success2`.
   - Otherwise enters `DONE`.

6. `NVME_QPAIR_AUTH_STATE_AWAIT_SUCCESS2` / `AWAIT_FAILURE2`
   - Waits for final send completion and then enters `DONE`.

7. `NVME_QPAIR_AUTH_STATE_DONE`
   - Cleans fabric poll resources and invokes auth cleanup.

A reentrancy guard, `auth->flags.in_auth_poll`, prevents recursive polling.

## Message Construction and Validation

- `nvme_auth_send_negotiate()` builds a common `AUTH_negotiate` message with a single DH-HMAC-CHAP descriptor.
- `nvme_auth_check_message()` validates expected message IDs and handles `AUTH_failure1` from the controller.
- `nvme_auth_check_challenge()` validates the DH-HMAC-CHAP challenge payload.
- `nvme_auth_send_reply()` computes the host response and optionally a controller challenge for bidirectional authentication.
- `nvme_auth_check_success1()` verifies controller response when a controller key is configured.
- `nvme_auth_send_failure2()` sends a terminal failure message when protocol/payload validation fails.

All auth send/receive commands use `nvme_auth_submit_request()`, which reuses `qpair->reserved_req` and `qpair->fabric_poll_status->dma_data`.

## Cryptographic Flow

`nvme_auth_get_key()` reads a key from `struct spdk_key` and expects the `DHHC-1:%02x:<base64>:` format. It:

1. Extracts the hash ID.
2. Decodes the base64 secret.
3. Requires decoded size of 36, 52, or 68 bytes, representing 32/48/64-byte keys plus a 4-byte CRC.
4. Validates CRC32.
5. Calls `nvme_auth_transform_key()`.

`nvme_auth_transform_key()` either copies raw key material for hash `NONE` or computes an HMAC over the NQN plus the literal NVMe-over-Fabrics string using the requested digest.

`spdk_nvme_dhchap_calculate()` computes the DH-HMAC-CHAP response over:

- Augmented challenge value.
- Sequence number.
- Transaction ID.
- Secure channel concatenation byte.
- Role string, such as `HostHost` or `Controller`.
- Local and remote NQNs with a zero terminator between them.

If a DH group is not `null`, `spdk_nvme_dhchap_generate_dhkey()`, `spdk_nvme_dhchap_dhkey_get_pubkey()`, and `spdk_nvme_dhchap_dhkey_derive_secret()` use OpenSSL EVP_PKEY/DHX APIs to generate and derive the shared secret.

## State, Memory, and Secret Handling

- Authentication allocates `struct nvme_completion_poll_status` and a 4096-byte DMA buffer per qpair auth attempt.
- Sensitive temporary key buffers are zeroed with `spdk_memset_s()`.
- `spdk_key_dup()` is used while holding the controller lock, then key references are released with `spdk_keyring_put_key()`.
- The file logs public keys and DH secret dumps through auth debug logging macros, which is useful for debugging but sensitive if debug log collection is enabled in production-like environments.

## Important Dependencies

- OpenSSL EVP MAC, EVP PKEY, DHX, RAND, BIGNUM, and OSSL_PARAM APIs.
- SPDK key/keyring abstractions.
- SPDK base64, CRC32, endian, and secure memset utilities.
- NVMe-oF fabric authentication structures from SPDK internal/public headers.
- Common completion polling from `nvme.c`.

## Error Handling and Risks

- Missing host DH-HMAC-CHAP key returns `-ENOKEY`.
- Secure channel concatenation is explicitly unsupported and returns `-EINVAL`.
- Protocol validation failures generally send `failure2` if possible and complete with `-EACCES`.
- Unsupported/disallowed digest or DH group is treated as authentication failure.
- OpenSSL allocation or crypto operation failures generally return `-EIO`, `-EINVAL`, `-ENOMEM`, or `-ENOBUFS`.
- Bidirectional authentication requires a host key; controller-key-only configurations are rejected elsewhere in controller key setup.

## Filesystem/Virtualization Relevance

This file secures NVMe-oF controller/qpair connections used by SPDK storage applications. In virtualized storage deployments, this authentication path protects remote block-device attachment and controller access.
