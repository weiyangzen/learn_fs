# sources/sync-backup/rsync/authenticate.c

Purpose: implements rsync daemon challenge-response authentication.

Important APIs/types/functions: public `base64_encode()` and `auth_client()` plus server-side `auth_server()`; helpers `gen_challenge()`, `generate_hash()`, `check_secret()`, and `getpassf()`.

Control flow: server negotiates auth checksum, creates a time/pid/address challenge, reads `user response`, matches configured auth users or groups with optional `:deny`, `:ro`, `:rw`, verifies secrets file permissions and hashed password, zeros sensitive buffers, and returns authenticated username or NULL. Client chooses password file, `RSYNC_PASSWORD`, or interactive prompt, hashes password+challenge, and sends response.

State and persistence: reads secrets/password files and environment; mutates global `read_only` based on auth rule. Sensitive buffers are wiped where practical.

Dependencies/integration: uses daemon config, checksum negotiation from `checksum.c`, uid/gid group lookup, wildcard matching, IO protocol helpers, and cleanup exits.

Risks: file permission checks are security-critical. `getpass()` may truncate on some systems. Hash strength depends on negotiated digest availability.

Test signals: daemon auth tests and TCP CI runs exercise this path; checksum negotiation tests indirectly protect digest choices.
