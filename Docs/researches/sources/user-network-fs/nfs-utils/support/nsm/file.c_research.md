# sources/user-network-fs/nfs-utils/support/nsm/file.c

Purpose: `file.c` owns NSM/statd durable state: state number files, monitored-host records, notify-backup records, privilege dropping, and monitor record load/delete/retire operations.

Important APIs and control flow: Path helpers validate hostnames and construct paths under `nsm_base_dirname`. `nsm_get_state` reads and optionally advances the odd NSM state number via atomic write, and `nsm_update_kernel_state` posts it to `/proc/sys/fs/nfs/nsm_local_state`. `nsm_insert_monitored_host`, `nsm_load_monitor_list`, `nsm_load_notify_list`, `nsm_delete_monitored_host`, and `nsm_delete_notified_host` serialize or parse text records containing callback address, RPC tuple, private cookie, mon_name, and my_name. `nsm_drop_privileges` changes to the state directory owner and preserves only bind-service capability when possible.

State, dependencies, and integration: Durable files live in `sm`, `sm.bak`, and `state`; updates use temp-file rename. It depends on libcap/prctl, `generic_*` path helpers, xlog, NSM XDR structs, and statd monitor callbacks.

Risks and test signals: Records only encode IPv4 callback addresses, append/delete rewrites are not locked, malformed records can abort a load, and privilege logic depends on directory ownership. Tests should cover atomic state updates, reboot retirement, multi-record host files, bad hostnames, corrupted lines, non-root state directories, and kernel-state write failures.
