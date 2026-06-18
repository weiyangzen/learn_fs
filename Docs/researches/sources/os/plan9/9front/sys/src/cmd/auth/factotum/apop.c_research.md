# File Research: sources/os/plan9/9front/sys/src/cmd/auth/factotum/apop.c

Factotum protocol module for APOP and CRAM-MD5 challenge/response authentication.

Key responsibilities:
- Implements shared state machine for `apop` and `cram`.
- Client mode accepts a challenge, finds a password key, and returns an MD5 or HMAC-MD5 response.
- Server mode obtains a challenge from the Plan 9 auth server, receives user/response, and validates via authsrv.
- Produces `AuthInfo` on successful server-side validation.
- Disables a server key after an auth-server protocol failure if it has never succeeded.

Dependencies:
- Uses factotum `Proto`, key lookup, authsrv requests/responses, MD5/HMAC-MD5, and ticket/authenticator conversion helpers.

Notable risks:
- Client mode does not authenticate the server.
- Response size is fixed to hex MD5 length.
