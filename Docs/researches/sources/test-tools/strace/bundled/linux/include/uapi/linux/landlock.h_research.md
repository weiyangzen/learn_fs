# sources/test-tools/strace/bundled/linux/include/uapi/linux/landlock.h

Purpose: defines the Landlock sandboxing syscall ABI for creating rulesets, adding path/network rules, and restricting the current process or thread group.

Important APIs/types/functions: key types are `landlock_ruleset_attr`, `landlock_path_beneath_attr`, `landlock_net_port_attr`, `enum landlock_rule_type`, create/restrict flags, filesystem access bits, network access bits, and scope bits for abstract UNIX sockets and signals.

Control flow: applications query ABI/errata with `landlock_create_ruleset`, create a ruleset with handled access masks, add `PATH_BENEATH` and `NET_PORT` rules, then call `landlock_restrict_self` optionally with logging or thread-sync flags. Later filesystem, TCP, UNIX socket, signal, and ioctl decisions are mediated by the enacted domain.

State/persistence behavior: ruleset fds persist until closed; enacted Landlock domains are process/thread security state and are restrictive, stackable, and inherited across fork/exec according to kernel semantics. Logging flags affect audit behavior.

Dependencies/integration: depends on `linux/types.h` and integrates with LSM hooks, audit, `no_new_privs`, mount/path resolution, TCP sockets, and UNIX IPC.

Risks and test signals: versioned ABI and default-denied `REFER` semantics are subtle. Tests should cover ABI version queries, packed path rules, TCP port 0 behavior, scoped IPC flags, logging flags, TSYNC, and unknown access-bit compatibility.
