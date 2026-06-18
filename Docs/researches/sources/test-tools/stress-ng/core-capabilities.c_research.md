# sources/test-tools/stress-ng/core-capabilities.c

Purpose: Linux capability/root privilege checking and capability dropping.

Important APIs and control flow: `stress_check_root` checks `geteuid` and Cygwin administrator groups; `stress_capabilities_getset` round-trips current capability sets; `stress_capabilities_check` checks requested permitted capability or root fallback; `stress_capabilities_drop` clears inheritable/permitted/effective capability bits through `capset` and enables `PR_SET_NO_NEW_PRIVS` when supported.

State and persistence: mutates current process credentials/capability state; no file persistence.

Dependencies and integration: uses Linux capability syscalls/headers, `prctl`, Cygwin `getgroups`, and stress-ng logging.

Risks and test signals: dropping capabilities is irreversible for the process; fallback-to-root semantics can over-approximate capabilities on non-Linux. Signals are privileged/unprivileged stressor gating and post-drop inability to regain privileges.
