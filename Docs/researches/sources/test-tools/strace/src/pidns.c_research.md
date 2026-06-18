<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/pidns.c -->
# sources/test-tools/strace/src/pidns.c

Purpose: translates and annotates PIDs across PID namespaces for decoded output.

Important APIs/types/functions: `pidns_init`, `translate_pid`, `get_proc_pid`, `printpid`, `printpid_tgid_pgid`, `get_ns_hierarchy`, `get_id_list`, trie caches `ns_pid_to_proc_pid` and `proc_data_cache`, and `struct proc_data`.

Control flow: initialization sizes trie caches from `/proc/sys/kernel/pid_max`. Translation first handles trivial same-namespace cases, then checks cached namespace/id mappings, validates cached process data, scans cached entries, and finally scans `/proc` and task directories. Namespace hierarchy is walked with `NS_GET_PARENT`; status files provide `NSpid`/`NStgid`/`NSpgid`/`NSsid` lists.

State and persistence behavior: process-wide trie caches persist namespace-to-proc-pid mappings and per-proc namespace/id hierarchies. `ns_get_parent_enotty`, `pid_max`, and cached namespace ids persist to avoid repeated expensive probes.

Dependencies and integration points: used by `printpid`, fd/path helpers, namespace ioctls, and decode-pid options; depends on `/proc`, nsfs ioctls, trie implementation, number sets, largefile wrappers, and tcb `pid_ns`.

Risks: heavy reliance on `/proc` visibility, permissions, kernel namespace ioctl support, and process liveness. Cache invalidation is best-effort and must handle disappearing processes.

Test signals: same namespace fast path, nested PID namespaces, proc-pid lookup, cache hits/invalidations, missing `NS_GET_PARENT`, permission failures, comm annotations, TGID/PGID/SID translation, and disabled decode-pid options.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/pidns.c -->
