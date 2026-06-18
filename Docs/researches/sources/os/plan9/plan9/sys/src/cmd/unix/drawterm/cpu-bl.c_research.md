# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/cpu-bl.c

Read fully: 730 lines, 14388 bytes. SHA-256 prefix: `18e665a404a49810`.

This is the Bell Labs-default variant of drawterm’s CPU client connection code. It dials a CPU server, negotiates authentication/encryption, sends optional command and working directory, waits for remote export setup, then runs local `exportfs()` over the connection.

Important behavior:
- Defaults `authserver` to `p9auth.cs.bell-labs.com` and `system` to `plan9.bell-labs.com`.
- Supports options for auth server, CPU server, clear/encrypted algorithms, command, key spec, root base, secstore, and user.
- `mountfactotum()` tries to mount factotum and falls back to secstore retrieval.
- `rexcall()` dials TCP port `17010`, negotiates auth method and algorithms, then calls the selected auth method.
- `netkeyauth()` implements manual challenge/response.
- `p9auth()` runs `p9any`, exchanges nonces, derives SHA1 secrets, and pushes SSL/RC4 if enabled.
- `p9any()` uses factotum if available, otherwise performs p9sk1 ticket/authenticator exchange manually.

Risk notes: server-side auth functions are stubs returning `-1`; this is client-focused.
