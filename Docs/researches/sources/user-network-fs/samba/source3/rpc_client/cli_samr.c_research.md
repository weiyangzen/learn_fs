# sources/user-network-fs/samba/source3/rpc_client/cli_samr.c research

## Purpose

`cli_samr.c` implements source3 convenience helpers for the SAMR RPC interface. Its main responsibility is password-change preparation: it transforms plaintext old/new passwords or caller-provided blobs into the encrypted structures expected by SAMR change-password operations, invokes generated NDR SAMR calls, returns transport NTSTATUS separately from server result NTSTATUS, and wipes sensitive intermediate material. It also provides display-info pagination parameters and a compatibility sequence for SAMR connect variants.

## Important APIs, types, and functions

Password helpers include `dcerpc_samr_chgpasswd_user()` and `rpccli_samr_chgpasswd_user()` for handle-based `ChangePasswordUser`; `dcerpc_samr_chgpasswd_user2()` and `rpccli_samr_chgpasswd_user2()` for username-based `ChangePasswordUser2`; `dcerpc_samr_chng_pswd_auth_crap()` and its `rpccli_` wrapper for precomputed blobs; `dcerpc_samr_chgpasswd_user3()` and its wrapper for `ChangePasswordUser3` with domain/reject details; and `dcerpc_samr_chgpasswd_user4()` for the AES-based password change path.

Utility helpers are `dcerpc_get_query_dispinfo_params()` and `dcerpc_try_samr_connects()`. The file uses `samr_Password`, `samr_CryptPassword`, `samr_EncryptedPasswordAES`, `lsa_String`, `policy_handle`, `samr_DomInfo1`, and `userPwdChangeFailureInformation`.

## Control flow

The older password-change flows calculate NT hashes with `E_md4hash()` and, if permitted and possible, LM hashes with `E_deshash()`. They derive old-password-encrypted hash fields with `E_old_pw_hash()` and construct `samr_CryptPassword` buffers with `init_samr_CryptPassword()`, using the old NT hash as the session key for the crypt-password encoding. They then call generated SAMR operations such as `dcerpc_samr_ChangePasswordUser`, `ChangePasswordUser2`, or `ChangePasswordUser3`.

The `rpccli_` wrappers call the `dcerpc_` variants using `cli->binding_handle` and `cli->srv_name_slash`, then return the server-side `result` if the transport call succeeded. This preserves the Samba pattern where an RPC transport failure and an application-level SAMR failure are distinguished.

`dcerpc_samr_chgpasswd_user4()` implements the AES/HMAC-SHA512 password-change mechanism. It generates a random salt, derives a content-encryption key from the old NT hash and salt using PBKDF2-SHA512 with a random iteration count between 5000 and 1000000, encodes the new password into a 514-byte Unicode buffer, encrypts it with `samba_gnutls_aead_aes_256_cbc_hmac_sha512_encrypt()`, fills `samr_EncryptedPasswordAES`, and calls `dcerpc_samr_ChangePasswordUser4()`.

`dcerpc_try_samr_connects()` attempts `Connect5`, then `Connect4`, then `Connect2`, returning as soon as both transport status and SAMR result are success. `dcerpc_get_query_dispinfo_params()` returns empirically chosen `max_entries` and `max_size` values for repeated QueryDisplayInfo calls.

## State and persistence behavior

The file maintains no persistent state. It allocates temporary encrypted structures under the caller's talloc context and explicitly zeroes or burns plaintext hashes, LM/NT hash arrays, crypt-password buffers, AES keys, and password buffers before returning where implemented. Returned domain info or reject structures are allocated by the generated NDR call under the caller's `mem_ctx`.

## Dependencies and integration points

Dependencies include generated `ndr_samr_c` stubs, `rpc_client/rpc_client.h`, SAMR/LSA initialization helpers, legacy auth crypto helpers from `libcli_auth`, Samba GnuTLS helpers, and runtime configuration such as `lp_client_lanman_auth()`. The file integrates with `cli_pipe.c` through `struct rpc_pipe_client->binding_handle` and `srv_name_slash`.

## Risks and edge cases

This file handles plaintext passwords and derived hashes. The main risks are incomplete secret wiping on early returns, incorrect LM-hash behavior for long passwords, cryptographic API failures mapped to policy-like NTSTATUS values, and ensuring `presult` is meaningful only when the transport status is OK. The AES path defines `old_nt_key.size` with `sizeof(old_nt_key)`, not the size of the 16-byte key buffer; that is a subtle implementation detail worth targeted review because PBKDF2 input length must be exactly what the protocol expects.

Blob-based `dcerpc_samr_chng_pswd_auth_crap()` silently leaves zeroed fields when blobs are missing or shorter than expected; callers must validate blob provenance. `dcerpc_try_samr_connects()` keeps the final transport status even when earlier server results failed, so callers must inspect `presult`.

## Test signals

Tests should cover password changes with NT-only and LM-enabled configurations, long passwords that disable LM hashes, generated crypto failure paths, wrapper behavior that returns server result after successful transport, `ChangePasswordUser3` reject/domain-info outputs, AES `ChangePasswordUser4` with known test vectors if available, zeroization under failure, and SAMR connect fallback against servers supporting only Connect2 or Connect4.
