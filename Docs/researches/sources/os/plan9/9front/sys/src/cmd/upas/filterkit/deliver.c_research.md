# File Research: sources/os/plan9/9front/sys/src/cmd/upas/filterkit/deliver.c

This command appends stdin to a target mailbox for a recipient, using a from-address file.

Key behavior:
- Usage: `deliver recipient fromaddr-file mbox`.
- Extracts local recipient after last `!`.
- Reads first address from the from-address file via `readaddrs`.
- Appends stdin fd `0` to target mailbox with `fappendfolder`.
- Logs delivery result with recipient, from address, current date, original recipient argument, return code, and error string.

Integration and risks:
- Depends on common folder append semantics and locking.
- Exits with empty status even after logging `r`; failures are not directly propagated through a non-empty exit string.
