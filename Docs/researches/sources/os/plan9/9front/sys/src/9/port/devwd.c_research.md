# File Research: sources/os/plan9/9front/sys/src/9/port/devwd.c

Implements a small watchdog device `#w` with `wdctl`. Platform watchdog backends register through `addwatchdog`, which installs a single global `Watchdog` and disables it initially.

Reads from `wdctl` call the backend `stat` hook if present. Writes accept `enable`, `disable`, and `restart`, dispatching to the backend hooks. The device otherwise uses standard device helpers for attach, walk, stat, open, remove, wstat, and power.

Important behavior: writes reject nonzero offsets or messages larger than `READSTR`; unknown commands return `Ebadarg`. The file assumes the write buffer is mutable when it truncates at newline.
