# File Research: sources/os/bsd/freebsd-src/sbin/reboot/reboot.c

Implementation shared by `reboot`, `halt`, `fastboot`, `fasthalt`, and `nextboot`.

Key elements:
- Program behavior is selected from `getprogname`: `fast*` enables fast shutdown, `halt` sets halt mode, `nextboot` switches to nextboot option parsing.
- `zfsbootcfg` invokes `zfsbootcfg` to set `nextboot_enable=YES` in ZFS nvstore.
- `write_nextboot` atomically writes `/boot/nextboot.conf`, optionally preserving old content, writing `nextboot_enable` for UFS, adding kernel/env settings, fsyncing, and renaming the temp file.
- `split_kv` parses `name=value` option strings, including quoted values.
- `add_env` appends boot environment assignments to a generated buffer.
- `shutdown` signals init with the signal corresponding to reboot/halt/poweroff/powercycle/reroot.
- `main` validates option combinations, handles nextboot deletion/writes, checks root permissions for reboot modes, logs shutdown intent, writes utmpx shutdown time, syncs, signals init/processes, waits for paging activity to settle, sends SIGKILL if needed, and calls `reboot`.
- `get_pageins` reads `vm.stats.vm.v_swappgsin` to decide whether to wait longer before SIGKILL/reboot.

Dependencies:
- FreeBSD reboot flags, boottrace, sysctl, syslog, utmpx, process signals, `/boot/nextboot.conf`, optional `zfsbootcfg`.

Research notes:
- `nextboot` does not require root until actual reboot paths; it writes nextboot configuration and exits.
- `-D` only deletes existing nextboot config and refuses combination with other actions.
- `add_env` checks `env == NULL` after `asprintf`, but `env` is the address of the caller pointer; the intended failure check is likely `*env == NULL`.
