# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_crashme.c

Read completely: 375 lines.

Provides deliberate crash/debug sysctl hooks under `debug.crashme` for testing kernel panic, fault, debugger, lock, SPL, and preemption failure paths. A separate writable `debug.crashme_enable` gate must be enabled before actions execute.

`crashme_add()` dynamically registers a named crashme sysctl node, avoiding duplicates and appending it to the linked list. `crashme_remove()` unlinks and destroys a registered node. `crashme_sysctl_forwarder()` maps the sysctl node number back to a `crashme_node`, handles read/list behavior through `sysctl_lookup()`, checks the enable gate for writes, invokes the node handler, and panics if the handler unexpectedly reports failure. `SYSCTL_SETUP()` creates the root node, enable boolean, mutex, and built-in crash nodes.

Built-in handlers include plain `panic()`, null pointer write, null function call, optional DDB entry, optional kernel-lock spinout, mutex recursion, infinite spin at raised IPL, and infinite spin with kernel preemption disabled.

Risks and notes: this file is intentionally destructive when enabled. `crashme_remove()` appears to print “unable to remove” when `sysctl_destroyv()` returns zero, which is usually success. The event handlers contain intentionally unreachable cleanup after infinite loops or deliberate crash paths.
