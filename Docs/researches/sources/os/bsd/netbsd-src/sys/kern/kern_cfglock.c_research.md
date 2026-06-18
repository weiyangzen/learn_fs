# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_cfglock.c

Read completely: 101 lines.

Provides the recursive kernel configuration lock used to serialize additions and removals of kernel functionality such as device configuration and module loading.

`kernconfig_lock_init()` initializes the backing mutex and owner/recurse state. `kernconfig_lock()` asserts it is not called from interrupt context, then either increments recursion for the current LWP or takes the mutex and records the owner. `kernconfig_unlock()` decrements recursion and releases the mutex when the outermost holder exits. `kernconfig_is_held()` reports whether the backing mutex is owned.

Risks and notes: recursion ownership is tracked manually with `kernconfig_lwp` and `kernconfig_recurse`, so correct pairing is essential. The unlocked current-LWP owner check is documented as safe only because the owner can be set to `curlwp` by the current thread itself, not by interrupts or other LWPs.
