# File Research: sources/os/plan9/9front/sys/src/cmd/auth/secstore/secuser.c

Interactive account-management tool for secstore users. It creates required secstore directories, creates or updates `PW` records, sets password verifier data, expiration, enabled/disabled status, STA requirement, and comments.

Important behavior:
- `ensure_exists()` creates `/adm/secstore`, `/adm/secstore/who`, and `/adm/secstore/store` when missing.
- Existing users are loaded with `getPW(id, 1)`; missing users allocate a new `PW`.
- Password input enforces minimum 7 characters unless updating an existing user and leaving password blank.
- New password is converted into PAK verifier `Hi` through `PAK_Hi`.
- Expiration date is entered as `DDMMYYYY`, stored as end-of-day local epoch seconds.
- Failed login count is cleared.
- Status bits are interactively toggled for `Enabled` and `STA`.
- Writes account data using `putPW`; creates per-user store directory for new users with `0775`.

Filesystem relevance:
- Initializes and mutates the secstore administrative tree under `/adm/secstore`.
- Creates per-user file-store directories after successful account write.
