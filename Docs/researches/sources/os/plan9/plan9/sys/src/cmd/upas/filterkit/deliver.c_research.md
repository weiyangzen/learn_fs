# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/filterkit/deliver.c

- Role: Delivery helper that appends stdin to a mailbox with locking and logging.
- Control flow: Parses recipient/fromfile/mbox, extracts delivered-to local name, reads sender address, takes mailbox lock, appends `From sender date` plus message content, unlocks, and syslogs delivery.
- Integration: Uses `readaddrs`, `syslock`, `appendfiletombox`, and upas common wrappers.
- Risks/notes: If `syslock` returns nil, delivery continues without checking; mailbox open retries only for exclusive lock errors.
