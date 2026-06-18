# File Research: sources/os/bsd/netbsd-src/lib/libtelnet/auth.c

## Purpose
Implements Telnet Authentication option negotiation and dispatch across compiled authenticator methods.

## Main Interfaces
Exports authenticator lookup, init, enable/disable/status/debug commands, authentication request/send/is/reply/name handling, completion state, wait logic, and suboption formatting.

## Control Flow And State
The `authenticators[]` table lists supported methods in priority order: Kerberos V5 mutual/one-way when compiled, then SRA when compiled. Global state tracks local name, server/client role, supported and disabled type masks, current authentication attempt, final authenticated method, and user validity level.

Server-side `auth_request` sends `TELQUAL_SEND` with all locally supported and not-disabled method/type pairs. Client-side `auth_send` stores the remote offered list, scans it in order, finds a matching local authenticator, and calls its `send` function. If none work, it sends `AUTHTYPE_NULL` and marks authentication rejected.

`auth_is` handles server-side `TELQUAL_IS` payloads by dispatching to a method `is` handler. `auth_reply` handles client-side replies. `auth_name` records the login name for encryption/auth modules. `auth_sendname` emits a TELQUAL_NAME suboption with IAC escaping.

`auth_wait` spins the telnet application until authentication completes or a 30-second alarm fires, then asks the selected authenticator to finalize status if available.

## Dependencies
Uses `<arpa/telnet.h>` auth constants, `telnet_net_write`, `telnet_spin`, `printsub`, method implementations, and `auth_encrypt_user`.

## Risks And Notes
Global state makes the dispatcher connection-oriented rather than instance-safe. `auth_send` has delicate pointer logic for saved offer lists and retry. The wait path uses process `SIGALRM`, which can interfere with applications using alarms.
