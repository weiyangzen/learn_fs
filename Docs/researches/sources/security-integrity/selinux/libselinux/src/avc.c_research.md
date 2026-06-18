# sources/security-integrity/selinux/libselinux/src/avc.c

Purpose: `avc.c` implements the userspace SELinux Access Vector Cache. It interns security contexts as `security_id_t`, caches access vector decisions by `(ssid, tsid, class)`, audits decisions, and reacts to policy/enforcing changes through callbacks and status notifications.

Important APIs/types/functions: public APIs include `avc_open()`, `avc_init()`, `avc_destroy()`, `avc_context_to_sid[_raw]()`, `avc_sid_to_context[_raw]()`, `avc_get_initial_sid()`, `avc_has_perm[_noaudit]()`, `avc_compute_create()`, `avc_compute_member()`, callback registration, stats, and security-server update handlers `avc_ss_*`. Core types are `avc_entry`, `avc_node`, `avc_cache`, callback nodes, and the `sidtab`.

Control flow: initialization configures optional memory/log/thread/lock callbacks, allocates locks, initializes fixed cache slots and freelist nodes, sets enforcing state, initializes the SID table, allocates audit buffer, and opens SELinux status mapping. Permission checks first consult an entry reference, then cache, then `security_compute_av_flags_raw()`, inserting the decision if current. Denied bits are allowed in permissive mode or per-domain permissive decisions. Audited events are formatted with class/permission names and supplemental audit callbacks. Policy/enforcement updates reset or patch cache entries and notify registered callbacks.

State and persistence: state is entirely process-local: cache buckets, freelist, callback list, audit buffer, stats, SID table, latest notification sequence, enforcing flag, and running flag. It persists until `avc_destroy()` and is invalidated by status/netlink events.

Dependencies and integration: depends on `selinuxfs` compute APIs, class/permission mapping, `selinux_status_*`, `avc_internal` callbacks, and `avc_sidtab`. Object managers use it through libselinux AVC APIs.

Risks and test signals: cache correctness depends on locking, sequence-number checks, and policyload/setenforce invalidation. The empty `avc_cleanup()` means reclaim behavior is bounded by initial freelist plus reclaim scan. Tests should cover cache hit/miss/ref discard, permissive handling, unknown classes, callback retention for try-revoke, audit output, status-triggered reset, and destroy/reinit.
