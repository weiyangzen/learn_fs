# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/devroot.c

Implements the synthetic root device `#/`.

Key behavior:
- Builds static root, boot, and mnt directory lists.
- Root initially contains `boot`, `mnt`, plus directories added in `rootreset`: `bin`, `dev`, `env`, `fd`, `net`, `net.alt`, `proc`, `root`, and `srv`.
- `mnt` contains `factotum`.
- `addbootfile` adds in-memory files under `boot`.
- Directory reads use `rootgen`; regular boot/mnt file reads copy from stored in-memory data.
- Writes are rejected.

Important interfaces:
- `addbootfile` is an external helper for boot-time synthetic files.
- `rootdevtab` registers device character `/`.

Notable risks:
- Directory capacities are fixed (`Nrootfiles`, `Nbootfiles`, `Nmntfiles`).
- Some fallback logic in `rootread` defaults non-boot/non-mnt files to `bootlist`, but normal access should be constrained by generated qids.
