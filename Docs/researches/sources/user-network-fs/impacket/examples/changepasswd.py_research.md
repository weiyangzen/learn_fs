# sources/user-network-fs/impacket/examples/changepasswd.py

## Purpose
`changepasswd.py` is a multi-protocol Active Directory password change and reset utility. It exposes a single CLI over several back ends: SAMR over SMB named pipe, SAMR over endpoint-mapped TCP RPC, Kerberos kpasswd, and LDAP/LDAPS `unicodePwd` modification. It supports self-service password changes using old credentials and privileged password resets using `-reset` with optional alternate credentials.

## Important APIs, Types, and Functions
The central abstraction is `PasswordHandler`, whose public `changePassword()` and `setPassword()` methods normalize target and authenticator identities before delegating to `_changePassword()` and `_setPassword()`. `KPassword` wraps `impacket.krb5.kpasswd.changePassword()` and `setPassword()`. `SamrPassword` manages DCE/RPC authentication, SAMR binding, user handle lookup, and common SAMR error mapping through `_SamrWrapper()`. `RpcPassword` and `SmbPassword` only provide transport selection through `epm.hept_map()` and `transport.SMBTransport`. `LdapPassword` uses `ldap.LDAPConnection`, `ldapasn1.ModifyRequest`, and Microsoft `unicodePwd` quoting/UTF-16LE encoding.

`parse_args()` defines credential, alternate credential, new password/hash, Kerberos, and protocol options. The main block uses `parse_target()` and `EMPTY_LM_HASH`, prompts via `getpass`, splits LM/NT hashes, forces Kerberos for kpasswd, instantiates the selected handler, and exits with the handler result.

## Control Flow
Startup selects a protocol handler from `handlers`, parses the target account, decides the target domain default (`Builtin` for SAMR, address for LDAP/kpasswd), gathers old and new secrets, and derives authenticator credentials from either `-altuser` or the target identity. For password changes, `PasswordHandler.changePassword()` defaults missing target, old password, and old hashes to the authenticating identity. For resets, `setPassword()` uses the privileged identity.

SAMR flow authenticates to DCE/RPC, optionally retries anonymously when an expired password blocks bind and plaintext new password allows `hSamrUnicodeChangePasswordUser2`, opens a user handle for hash changes or resets, then calls SAMR procedures. LDAP flow connects to LDAPS, finds the target DN by `sAMAccountName`, builds delete/add modifications for changes or replace modifications for resets, and interprets LDAP result codes. Kerberos flow requires plaintext new passwords and directly calls kpasswd helpers.

## State and Persistence
The script does not maintain durable application state. It mutates remote account password material and may create consequences in AD/Kerberos state: SAMR hash-based changes can mark passwords expired, SAMR resets with hashes can avoid policy/history and omit Kerberos key generation, and LDAP/kpasswd changes update server-side password state. Local state is in handler instance fields (`dce`, `ldapConnection`, credentials, base DN) and process exit status.

## Dependencies and Integration Points
This file integrates with Impacket DCE/RPC SAMR, EPM, SMB transport, Kerberos kpasswd, LDAP ASN.1, and OpenSSL-backed LDAPS errors. It relies on example logger formatting and target parsing shared by other Impacket examples. External integration points are domain controllers over SMB/RPC, Kerberos KDC/password-change service, and LDAPS.

## Risks
The tool handles plaintext passwords, NTLM hashes, AES keys, and privileged reset credentials on the command line and in memory. Wrong protocol selection can produce partial or policy-bypassing changes, especially hash-based SAMR resets. Anonymous retry for expired-password SAMR changes is intentionally narrow but depends on server policy. LDAP lookup by `sAMAccountName` returns the first matching search result. Debug logging can expose sensitive parameters because `_changePassword()` logs credential-related tuples.

## Test Signals
Useful tests include argument parsing for hash-only and plaintext modes, handler selection for each protocol, kpasswd plaintext enforcement, SAMR handling of known status strings, LDAP request shape for change versus reset, and exit code behavior. Integration tests require a controlled AD lab with expired accounts, policy-rejected passwords, reset rights, LDAPS enabled/disabled cases, and Kerberos credential cache/AES-key paths.
