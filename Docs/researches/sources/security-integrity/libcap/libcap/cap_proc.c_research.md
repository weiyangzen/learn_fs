## sources/security-integrity/libcap/libcap/cap_proc.c

Purpose: process capability, securebits, ambient/bounding, POSIX-thread syscall routing, IAB application, UID/GID helpers, and privileged launcher implementation.

Important APIs/functions: `cap_set_syscall`, `cap_get_proc`, `cap_set_proc`, `capgetp`, `cap_get_pid`, `capsetp`, `cap_get_bound`, `cap_drop_bound`, `cap_get_ambient`, `cap_set_ambient`, `cap_reset_ambient`, `cap_get_secbits`, `cap_set_secbits`, `cap_prctl`, `cap_prctlw`, `cap_set_mode`, `cap_get_mode`, `cap_setuid`, `cap_setgroups`, `cap_iab_get_proc`, `cap_iab_set_proc`, launcher setters, `_cap_chroot`, `_cap_launch`, and `cap_launch`.

Control flow: wraps raw syscalls in `syscaller_s` so libpsx can replace single-thread calls with all-thread semantics. Process getters/setters use `capget/capset`. Mode setting raises `CAP_SETPCAP`, clears ambient, locks securebits, drops bounding bits for no-priv, and clears effective caps before return. UID/GID helpers temporarily raise `CAP_SETUID`/`CAP_SETGID`, set keepcaps/groups/uids, then clear effective caps. IAB setters adjust inheritable first, optionally raise `CAP_SETPCAP`, reset and raise ambient, and drop bounding bits. Launcher forks with an error pipe, runs callback and requested credential/mode/IAB/chroot changes in the child, then execs or exits for function launch.

State/persistence: mutates kernel process/thread capability state, securebits, bounding and ambient sets, uid/gid/groups, chroot/cwd, child processes, and process name.

Dependencies/integration: Linux syscalls/prctl, libpsx weak/strong syscall override, pthread-aware semantics, `sys/securebits.h`, `fork`, `execve`, `pipe2`, and wait/error propagation.

Risks: security-critical sequencing; privilege drops often irreversible. Launcher stores caller-provided argv/env pointers, so lifetimes must outlive launch. Parent reports child setup failure through errno pipe but successful exec returns only PID.

Test signals: `cap_test`, Go `try-launching`, `b210613`, `b215283`, `iaber`, `setid`, psx signal/deadlock tests, and privileged mode/UID/GID/IAB integration tests.
