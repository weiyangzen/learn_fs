# File Research: sources/os/plan9/9front/sys/src/cmd/auth/guard.srv.c

Guard service for Securenet/SecurID-style challenge-response authentication.

Key responsibilities:
- Reads a username from stdin using null-terminated argument protocol.
- Generates a numeric challenge and writes a challenge/response prompt.
- Reads a response with a three-minute alarm timeout.
- Accepts either stored network DES-key response via `netcheck` or SecureID response via `secureidcheck`.
- Writes `OK` or `NO`, logs debug details, and updates auth keyfs bad/good logs.
- Extracts remote address from a service directory's `remote` file when provided.

Dependencies:
- Uses auth command helpers, `/lib/ndb/auth`, local ndb, NETKEYDB, `netcheck`, `secureidcheck`, `fail`, and `succeed`.

Notable risks:
- Debug logging masks only the PIN portion of responses to avoid logging full secrets.
