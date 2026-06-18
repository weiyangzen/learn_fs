# File Research: sources/os/plan9/9front/sys/src/9/port/initcode.c

Tiny first user program embedded into the kernel to construct the initial namespace and exec `/boot/boot`.

Key responsibilities:
- Binds core devices into `/dev`, `/fd`, `/env`, `/proc`, `/srv`, and `/shr`.
- Opens `/dev/cons` three times for standard input, output, and error.
- Executes `/boot/boot` with the provided boot argv.
- On exec failure, reads the error string and exits with that message.

Important behavior:
- The file warns not to add library calls because the whole text image must fit in one page and no data segment is available.
- It uses global string literals for mount paths and device specs, including `#σ` for shared memory.

Dependencies:
- Built into architecture startup paths as `initcode[]`.
- Uses Plan 9 user syscalls through libc stubs: `bind`, `open`, `exec`, `rerrstr`, `_exits`.

Notable risks:
- Size and data-segment constraints are strict; ordinary-looking additions can break boot.
