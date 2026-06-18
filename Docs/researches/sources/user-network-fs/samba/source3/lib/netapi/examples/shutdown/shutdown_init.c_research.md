# sources/user-network-fs/samba/source3/lib/netapi/examples/shutdown/shutdown_init.c

## sources/user-network-fs/samba/source3/lib/netapi/examples/shutdown/shutdown_init.c

Purpose: Demonstrates initiating remote shutdown through `NetShutdownInit()`.

Important APIs/types/functions: Accepts hostname, optional message, timeout, force-apps flag, and reboot-after-shutdown flag.

Control flow: Parses arguments, converts numeric flags with `atoi()`, calls `NetShutdownInit()`, prints error string on failure, and cleans up.

State and persistence behavior: Schedules remote machine shutdown/reboot state.

Dependencies and integration points: Pairs with `shutdown_abort`.

Risks: Destructive administrative operation. Weak numeric parsing and no confirmation make accidental shutdown easy.

Test signals: Use only in isolated integration tests with a short timeout and abort path coverage.
