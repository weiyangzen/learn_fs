# File Research: sources/os/linux/linux/fs/coda/sysctl.c

## Purpose
Registers and unregisters Coda runtime sysctls.

## Main Elements
- Sysctls under `coda`: `timeout`, `hard`, and `fake_statfs`.
- `coda_sysctl_init()`: registers the table once.
- `coda_sysctl_clean()`: unregisters the table and clears the saved header.

## Dependencies And Integration
Exposes globals declared in `coda_int.h`: `coda_timeout`, `coda_hard`, and `coda_fake_statfs`. Called from module init/exit in `psdev.c`.

## Risk Notes
`timeout` and `hard` directly affect signal interruption behavior in `coda_upcall()` waits. `fake_statfs` is privileged `0600`, reflecting that it can alter filesystem reporting behavior.
