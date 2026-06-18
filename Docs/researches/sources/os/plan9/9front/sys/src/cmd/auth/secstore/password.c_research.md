# File Research: sources/os/plan9/9front/sys/src/cmd/auth/secstore/password.c

Secstore account password-verifier file reader/writer.

Key responsibilities:
- Opens account files under `SECSTORE_DIR/who/<id>` after filename validation.
- Falls back to `FICTITIOUS` account when requested account is absent.
- Parses account fields: expiration, disabled status, STA flag, failed count, other data, and `PAK-Hi`.
- Rejects expired, disabled, corrupted, or temporarily locked accounts unless caller requests dead-or-alive editing.
- Resets failed counter after five minutes when lockout period passes.
- Writes updated account records with `putPW`.
- Frees `PW` structures and mpint verifier material.

Dependencies:
- Uses secstore path definitions, Plan 9 Biobuf, mpint parsing/formatting, and file mtimes.

Notable risks:
- Missing accounts deliberately map to a fictitious account to avoid leaking existence during PAK handling.
