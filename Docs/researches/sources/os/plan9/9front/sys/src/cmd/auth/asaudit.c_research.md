# File Research: sources/os/plan9/9front/sys/src/cmd/auth/asaudit.c

Authentication setup audit tool.

Key responsibilities:
- Reads hostowner and reports mismatch with current user.
- Opens ndb and checks that nvram `authdom` maps to an auth server.
- Reads nvram safe and validates authid/authdom expectations.
- Starts `auth/keyfs -r`, reads the keyfs AES key, and compares it with nvram.
- Checks factotum for an enabled `dp9ik` key matching nvram authdom/authid.
- Exercises factotum dp9ik server authentication using nvram or keyfs key material.

Dependencies:
- Uses nvram, keyfs, factotum rpc, dp9ik/PAK helpers, ndb, and authsrv ticket structures.

Research notes:
- Reports `GOOD`/`BAD` diagnostic lines rather than enforcing one exit-code-only result.
- It can fall back to testing keyfs when factotum does not match nvram.
