# sources/user-network-fs/samba/source4/libnet/libnet_passwd.c

## Purpose

`libnet_passwd.c` implements Samba4 libnet password change and administrator password-set operations over remote SAMR RPC. It supports end-user change-password flows that prove knowledge of the old password and privileged set-password flows that open a SAMR user handle and write one of several SAMR user-info password levels. The file is security-sensitive because it handles plaintext passwords, NT/LM hashes, RPC session keys, weak-crypto fallback, and FIPS-mode exceptions around legacy RC4 paths.

## Important APIs, Types, and Functions

Public entry points are `libnet_ChangePassword()` and `libnet_SetPassword()`, both dispatching on level enums declared in `libnet_passwd.h`.

Password change helpers:
- `libnet_ChangePassword_samr_aes()` builds `samr_EncryptedPasswordAES` for `samr_ChangePasswordUser4`, deriving a content-encryption key from the old NT hash with PBKDF2-SHA512 and a random salt.
- `libnet_ChangePassword_samr_rc4()` implements fallback calls in order: `samr_ChangePasswordUser3`, `samr_ChangePasswordUser2`, and `samr_OemChangePasswordUser2`, using RC4-encrypted password buffers plus NT/LM verifiers.
- `libnet_ChangePassword_samr()` connects to a domain PDC SAMR pipe and tries AES first; it falls back to RC4 only for unsupported-proc statuses and only if weak crypto is not disallowed.
- `libnet_ChangePassword_generic()` maps generic input to the SAMR path.

Password set helpers:
- `libnet_SetPassword_samr_handle_26()`, `_25()`, `_24()`, `_23()`, and `_18()` implement SAMR `SetUserInfo2` levels. Levels 26/25 use `encode_rc4_passwd_buffer()` with the transport session key. Levels 24/23 encode a 516-byte Unicode password buffer and encrypt it with ARCFOUR. Level 18 encrypts an NT hash with `sess_crypt_blob()`.
- `libnet_SetPassword_samr_handle()` tries levels 26, 25, 24, and 23 unless a specific `samr_level` is requested.
- `libnet_SetPassword_samr()` connects to SAMR, opens the connect/domain/user handles, then delegates to the handle-level setter.
- `libnet_SetPassword_generic()` maps generic input to the SAMR path.

## Control Flow

Change-password flow: connect to the PDC SAMR pipe with `LIBNET_RPC_CONNECT_PDC`, format the server as `\\<rpc-server>`, try the AES `ChangePasswordUser4` request, and return immediately on success or implemented failure. Only unsupported-procedure style errors enter the RC4 fallback path, and the fallback is blocked when `lpcfg_weak_crypto()` reports weak crypto disallowed.

Set-password flow: generic requests become SAMR requests; SAMR requests connect to the PDC SAMR pipe, call `samr_Connect`, `samr_LookupDomain`, `samr_OpenDomain`, `samr_LookupNames`, validate exactly one RID/type, call `samr_OpenUser`, then pass the open user handle to the level-dispatcher. Handle-level auto-dispatch attempts modern password-info levels first and continues only for info-class/parameter/enum-level incompatibility.

## State and Persistence Behavior

The file does not maintain persistent local state. Remote persistent state is the user's password and, for most set levels, the password-expired flag or copied `samr_UserInfo21` fields. It uses talloc contexts for RPC request buffers and explicitly unlinks/frees RPC pipes after use. Sensitive temporary data is partially scrubbed with `BURN_DATA()` and `data_blob_clear[_free]()` for AES keys, session keys, and password buffers, but the caller-provided plaintext password strings remain owned by the caller.

## Dependencies and Integration Points

This file depends on libnet RPC connection helpers, generated SAMR RPC stubs, `source3/rpc_client/init_samr.h` password-buffer helpers, GnuTLS PBKDF2/ARCFOUR/session crypto wrappers, Samba credential/config APIs, SAMR/LSA generated structures, and `auth/libcli_auth` hash helpers. Python bindings in `py_net.c` expose the generic change/set functions, and domain-join code reuses the SAMR-handle set-password path for machine-account provisioning.

## Risks and Edge Cases

The weak-crypto fallback boundary is critical: RC4/LM flows must not run when policy forbids them. Several branches convert GnuTLS failures to NTSTATUS and must avoid returning success after crypto setup failure. The set-password levels require the right `info21` presence or absence; wrong combinations intentionally return `NT_STATUS_INVALID_PARAMETER_MIX`. The code sometimes uses maximum SAMR access and broad network error propagation, so tests need real DC/SAMR behavior. Failure handling should also preserve useful `error_string` messages while not leaking secrets.

## Test Signals

Relevant signals include Python `net.change_password()` and `net.set_password()` behavior, domain-join machine-password paths, and integration tests against DCs with and without `ChangePasswordUser4` support. Strong regression tests should cover AES success, unsupported-AES fallback, weak-crypto-disallowed fallback refusal, forced SAMR level 18 from Python, invalid `info21` mixes, exact SAMR result propagation, and FIPS mode restoration after legacy crypto calls.
