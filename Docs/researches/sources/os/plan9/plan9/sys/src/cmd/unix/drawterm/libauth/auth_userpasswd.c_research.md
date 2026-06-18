# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauth/auth_userpasswd.c

This file implements legacy Plan 9 user/password authentication.

Key behavior:
- `auth_userpasswd` builds an `AuthInfo` from username/password by requesting a ticket from the auth server.
- `netresp` creates the DES-based response for a challenge.

Important details:
- Uses `passtokey`, `authdial`, ticket request/reply conversion, and authenticator conversion routines from `libauthsrv`.
- Produces `AuthInfo` fields from the returned ticket/authenticator.
