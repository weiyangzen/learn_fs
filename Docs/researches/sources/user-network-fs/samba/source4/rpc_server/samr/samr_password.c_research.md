# sources/user-network-fs/samba/source4/rpc_server/samr/samr_password.c

## Purpose

This file implements SAMR password change and password reset handling for the Samba AD DC RPC server. It supports legacy NTLM-hash based change paths, RC4/confounded password reset buffers, encrypted hash buffers, and AES-based password buffers, while routing the final update through `samdb_set_password()` so domain policy, password history, account state, and DSDB modules remain authoritative.

## Important APIs, Types, And Functions

`log_password_change_event()` builds an `auth_usersupplied_info` record and calls `log_authentication_event()` so SAMR password changes produce consistent audit records. `dcesrv_samr_ChangePasswordUser()` and `dcesrv_samr_OemChangePasswordUser2()` are intentionally not implemented. `dcesrv_samr_ChangePasswordUser4()` handles AES change using PBKDF2 over the old NT hash and caller-provided salt to produce a content decryption key. `dcesrv_samr_ChangePasswordUser_impl()` implements the shared `ChangePasswordUser2`/`3` logic: fetch old NT hash, decrypt the new password with RC4 under that hash, verify the old-password verifier, and call `samdb_set_password()` as the caller.

Reset helpers are used by `dcesrv_samr.c`: `samr_set_password()` decrypts `samr_CryptPassword` with the transport session key and RC4; `samr_set_password_ex()` decrypts a confounded MD5/ARCFOUR buffer; `samr_set_password_buffers()` decrypts encrypted NT/LM hash buffers with `sess_crypt_blob()` and sets hashes directly; `samr_set_password_aes()` decrypts `samr_EncryptedPasswordAES` with Samba's AES-256-CBC-HMAC-SHA512 helper and extracts the password blob.

## Control Flow

Password change calls first connect to SAMDB with system privileges because old password hashes are required for verification. The user is found through `authsam_search_account()` to stay aligned with authentication and bad-password accounting. Once the supplied old credential is verified, the code temporarily swaps the LDB `DSDB_SESSION_INFO` opaque to the caller's session, performs `samdb_set_password()`, restores the previous session info, and commits the transaction. Failures cancel the transaction and are logged.

`ChangePasswordUser4` validates the AES password buffer and PBKDF2 iteration range, derives the content decryption key from the old NT hash and salt, drops to caller privileges for `samr_set_password_aes(..., DSDB_PASSWORD_CHECKED_AND_CORRECT)`, burns the derived key buffer, and commits. The `ChangePasswordUser2` wrapper fills a `ChangePasswordUser3` request and reuses the shared implementation.

Reset helpers follow a simpler decrypt-then-set flow. They obtain or derive the correct session key, enforce weak-crypto policy for RC4 paths when transport encryption is absent, decrypt the supplied buffer in place or into temporary blobs, extract the cleartext password buffer, and call `samdb_set_password()` with either `DSDB_PASSWORD_RESET` or the supplied old-password-checked mode. AES and cleartext blobs are freed or zeroed after use where the code explicitly owns them.

## State And Persistence

Persistent state changes are made only by `samdb_set_password()` and related DSDB modules. This may update password hashes, supplemental credentials, password history, `pwdLastSet`, lockout/bad-password state, and policy-enforced metadata. The file also updates bad password counts through `authsam_update_bad_pwd_count()` on wrong-password outcomes. Runtime sensitive state includes old hashes, session keys, derived AES keys, decrypted password buffers, and temporary LDB session-info overrides inside transactions.

## Dependencies And Integration Points

The file integrates with SAMR generated types, DCE/RPC call/session helpers, SAMDB/DSDB password policy code, auth SAM lookup and bad password accounting, loadparm weak-crypto settings, GnuTLS cipher/PBKDF2/AEAD helpers, NTLM crypto helpers, messaging/audit logging, and password extraction helpers from Samba RPC libraries. It is called directly by SAMR `SetUserInfo` password levels and by generated SAMR password-change opnums.

## Risks And Edge Cases

This file is security-sensitive. Any mismatch in privilege restoration, transaction cancellation, constant-time verifier checks, weak-crypto enforcement, session key selection, or buffer wiping can create authentication bypass, password disclosure, or policy bypass risk. The RC4 paths intentionally enter FIPS lax mode and must always return to strict mode. `samr_set_password_buffers()` tolerates missing user session keys by using a random key to match Windows behavior, but that compatibility path can hide caller/session mistakes. Wrong user results are mapped to wrong password to avoid username disclosure. PBKDF2 iteration bounds and AES buffer parsing must stay aligned with the protocol.

## Test Signals

Important tests include SAMR password change 2/3/4 with correct and incorrect old passwords, nonexistent users, account lockout updates, policy rejection with reject info, weak-crypto disabled behavior with encrypted and unencrypted transports, password reset levels from `SetUserInfo`, AES reset/change buffer round trips, transaction rollback on decrypt or policy failure, audit log event presence, bad password count changes, and memory-sanitizer/leak checks for decrypted buffers and temporary session-info restoration.
