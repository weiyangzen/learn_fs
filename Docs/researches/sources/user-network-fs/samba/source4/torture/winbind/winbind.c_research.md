<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/winbind/winbind.c -->
# sources/user-network-fs/samba/source4/torture/winbind/winbind.c

## Purpose

This file is the winbind torture module entry point and contains Kerberos PAC comparison tests. It creates an in-process GENSEC client/server exchange, captures the PAC used to build session info, asks winbind to decode the same PAC, and compares winbind's `wbcAuthUserInfo` with Samba's internal Kerberos PAC decoder.

## Important APIs, Types, and Functions

- `struct pac_data` stores the PAC blob captured from the server session-info hook.
- `test_generate_session_info_pac()` decodes a PAC into `auth_user_info_dc`, sets authentication/session flags, calls `auth_generate_session_info()`, and saves the PAC in `auth_ctx->private_data`.
- `torture_decode_compare_pac()` calls `wbcAuthenticateUserEx()` with `WBC_AUTH_USER_LEVEL_PAC`, decodes the PAC internally with `kerberos_pac_logon_info()`, and compares scalar fields plus primary, group, extra, and resource SIDs.
- `torture_winbind_pac()` drives the GENSEC client/server update loop for GSSAPI, GSS-SPNEGO, or krb5.
- `torture_winbind_init()` registers struct, wbclient, and PAC sub-suites.

## Control Flow

The PAC test initializes machine server credentials, a minimal `auth4_context` with a custom PAC session-info callback, and GENSEC client/server contexts. The client uses command-line credentials; the server uses machine credentials. The chosen mechanism is started by SASL name or mechanism name, then client/server `gensec_update()` calls are alternated until authentication completes. After `gensec_session_info()`, the saved PAC blob is decoded by winbind and internally, and all important identity fields and SID ordering are checked.

## State and Persistence Behavior

No database or local file state is written. The test mutates in-memory authentication context state by storing `pac_data` under `auth_ctx->private_data` and stealing the PAC blob memory into it. It depends on live Kerberos credentials and winbind availability.

## Dependencies and Integration Points

The file depends on GENSEC, Kerberos PAC utilities, auth session-info generation, libwbclient PAC authentication, Samba command-line credentials, and loadparm GENSEC settings. It integrates with `torture_winbind_struct_init()` and `torture_wbclient()` in the top-level winbind suite.

## Risks and Edge Cases

The comparison assumes winbind and internal PAC decoding produce the same scalar fields, Unix-time conversions, and SID ordering. PACs without expected resource-group structures or environments without usable Kerberos credentials can fail before comparison. `wbcFreeMemory(info)` is called after success, but the `error` pointer from `wbcAuthenticateUserEx()` is not separately freed in this code path.

## Test Signals

Pass signals are successful GENSEC authentication for `GSSAPI`, `GSS-SPNEGO`, and `krb5`, successful winbind PAC authentication, successful internal PAC parsing, equal account/domain/time/counter fields, and exact SID sequence equivalence for account SID, primary group SID, domain groups, extra SIDs, and resource groups.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/winbind/winbind.c -->
