## sources/user-network-fs/nfs-utils/utils/statd/callback.c

Purpose: Services incoming NSM `SM_NOTIFY` calls and schedules local lockd callbacks when monitored peers reboot.

Important APIs/types/functions: Exports `sm_notify_1_svc`. It uses `statd_present_address`, `statd_matchhostname`, `ha_callout`, `nlist_clone`, and global lists `rtnl` and `notify`.

Control flow: On `SM_NOTIFY`, it records sender address, invokes HA callout, exits early if no hosts are monitored, scans runtime monitored entries for changed state and hostname/address match, updates entry state, clones it, and inserts the clone into the pending notify/callback queue.

State and persistence: Mutates in-memory `rtnl` entry state and queues callback work in `notify`. Persistent monitor files are not removed here; lockd continues monitoring until unmonitor.

Dependencies and integration: Runs under RPC dispatch from `statd.c`; callback queue is processed by `svc_run.c` and `rmtcall.c`.

Risks and test signals: DNS matching can block or misidentify peers; remote `mon_name` trust is limited. Tests should cover IP and hostname matches, unchanged states, empty monitor list, HA callout invocation, and cloned callback queue entries.
