# File Research: sources/os/bsd/dragonflybsd/sys/kern/subr_cpuhelper.c

Per-CPU helper thread framework for executing callbacks on a selected CPU through lwkt message ports.

Key responsibilities:
- Creates one fixed-CPU helper thread per CPU during `SI_SUB_PRE_DRIVERS`.
- Exposes `cpuhelper_initmsg()`, `cpuhelper_replymsg()`, and `cpuhelper_domsg()` for callback-message setup, reply, and synchronous dispatch.
- Replaces each helper port's `mp_putport` with `cpuhelper_putport()` to detect synchronous self-messages and execute them directly.
- Provides `cpuhelper_assert()` invariant checks for code that must run inside or outside a specific helper context.

Important behavior:
- A synchronous message sent to the current helper port is converted into a direct callback invocation and returns `EASYNC`, preventing self-deadlock.
- Helper threads loop forever on their message port and require every message to contain a non-NULL callback.

Dependencies:
- Depends on DragonFly lwkt threads, ports, messages, fixed-CPU thread creation, and `sys/cpuhelper.h`.

Notable risks:
- Self-referential callbacks execute in the caller's current stack/context, not through the normal queued helper loop.
- Initialization assumes all helper ports start with the same original `mp_putport` function.
- There is no teardown path; the helper array is lifetime-kernel state.
