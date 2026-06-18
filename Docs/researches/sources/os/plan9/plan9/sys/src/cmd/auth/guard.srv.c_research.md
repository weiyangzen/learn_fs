# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/guard.srv.c

Implements the guard network authentication service. It reads a user argument from fd 0, sends a numeric challenge prompt, reads a NUL-terminated response, and validates it with netkey or SecurID.

It uses `/lib/ndb/auth` plus local ndb data, extracts remote address from an optional connection directory, and logs debug failures without exposing the PIN portion of SecurID responses. Authentication success writes `OK`; failure writes `NO`, records failed login state, and exits failure.

The netkey check currently uses `NETKEYDB`; a commented block shows prior Plan 9 key fallback. Timeout is enforced with `alarm` and a notify handler.
