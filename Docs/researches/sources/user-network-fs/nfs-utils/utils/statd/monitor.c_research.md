## sources/user-network-fs/nfs-utils/utils/statd/monitor.c

Purpose: Implements NSM monitor registration and deregistration RPC procedures used by local lockd.

Important APIs/types/functions: Exports `sm_mon_1_svc`, `sm_unmon_1_svc`, `sm_unmon_all_1_svc`, `load_state`, and global `rtnl`. Uses `caller_is_localhost`, `nlist_*`, `nsm_insert_monitored_host`, `nsm_delete_monitored_host`, `nsm_load_monitor_list`, `statd_canonical_name`, and HA callouts.

Control flow: `SM_MON` rejects non-loopback callers and non-lockd callbacks, sanitizes `my_name`, rejects dangerous hostnames, canonicalizes monitored host, handles duplicates or cookie changes, persists a monitor record, and inserts/updates runtime list. `SM_UNMON` and `SM_UNMON_ALL` validate local caller, find matching runtime records, delete persistent records, call HA hooks, and remove list nodes.

State and persistence: Maintains runtime monitor list and stable NSM monitor records. Uses `MY_STATE` for responses.

Dependencies and integration: Tied to kernel lockd callback program/procedure numbers, nsm support library, custom hostname matching, and RPC dispatch.

Risks and test signals: Security depends on loopback checks and hostname sanitation. DNS failure prevents monitoring. Duplicate-cookie update behavior and `free(clnt)` on failure need coverage. Tests should simulate local/non-local RPC callers, bad program/proc, malicious hostnames, duplicate monitors, persistent insert/delete failures, and reload from state.
