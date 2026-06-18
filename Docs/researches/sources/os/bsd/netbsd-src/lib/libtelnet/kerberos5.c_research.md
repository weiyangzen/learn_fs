# File Research: sources/os/bsd/netbsd-src/lib/libtelnet/kerberos5.c

## Purpose
Implements Telnet Authentication Kerberos V5, including optional mutual authentication, DES session-key export to telnet encryption, and credential forwarding.

## Main Interfaces
Exports `kerberos5_init`, `kerberos5_send`, `kerberos5_is`, `kerberos5_reply`, `kerberos5_status`, `kerberos5_printsub`, and `kerberos5_forward` when `KRB5` is enabled.

## Control Flow And State
Global state includes Kerberos context, auth context, AP-REQ data, accepted ticket, forwarding flags, and a telnet suboption buffer. `Data` emits Kerberos auth suboptions with IAC escaping.

Client send obtains the default credential cache, initializes an auth context bound to the telnet socket, requests a host service AP-REQ for `RemoteHostName` with a checksum over auth type/way, sends TELQUAL_NAME, then sends `KRB_AUTH`.

Server `kerberos5_is` receives `KRB_AUTH`, initializes an auth context, builds the host service principal, verifies the AP-REQ and checksum, obtains the remote subkey or session key, optionally sends AP-REP for mutual authentication, checks `krb5_kuserok` for the requested user, sends accept/reject, and passes DES session keys to the encryption layer when compatible.

Forwarded credentials are accepted via `KRB_FORWARD`, written into a FILE credential cache for the target user under `/tmp/krb5cc_<uid>`, and acknowledged or rejected. Client-side `kerberos5_forward` builds TGT forwarding credentials and sends them after authentication if forwarding flags request it.

Reply handling accepts/rejects client auth, verifies mutual AP-REP before accepting mutual mode, installs the local DES session key for encryption, and processes forwarding acknowledgments.

## Dependencies
Depends on Kerberos 5 APIs, telnet auth/encrypt/misc layers, passwd database, `/tmp` credential caches, `krb5_kuserok`, and external telnet socket descriptor `net`.

## Risks And Notes
The code is built around legacy DES telnet encryption interop and exports DES session keys only for DES key types. Credential-cache paths are predictable and require correct ownership changes. Global Kerberos/auth state is not per-connection-safe.
