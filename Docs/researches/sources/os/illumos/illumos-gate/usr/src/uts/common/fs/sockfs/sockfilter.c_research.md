# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/sockfs/sockfilter.c

## Purpose
Implements the illumos socket filter framework: configured filter entries, loaded filter modules, per-socket filter instances, attach/detach, callback dispatch, deferred accepts, flow control, and filter data injection.

## Main Behavior
- Maintains global filter entry and filter module lists, plus a taskq-backed list for closing over-aged deferred connections.
- `sof_init()` initializes lists, locks, deferred-close taskq, and global kstats.
- `sof_setsockopt()` handles `SOL_FILTER` programmatic attach/detach through `FIL_ATTACH` and `FIL_DETACH`, serializing stack mutation with the fallback rwlock.
- `sof_getsockopt()` reports attached filters through `FIL_LIST`.
- Automatic filters attach during socket initialization; programmatic filters attach on request; passive accepted sockets inherit listener filters bottom-up.
- Filter entries are matched to `sockparams` socket tuples and inserted into per-sockparams automatic or programmatic filter lists with placement hints.
- Filter modules register/unregister through `sof_register()`/`sof_unregister()` and are demand-loaded from `SOCKMOD_PATH` when needed.
- `sof_entry_add()` and `sof_entry_remove_by_name()` coordinate with `sockparams` under `sockconf_lock`.
- Per-socket filter instances form a top-to-bottom stack and hold references to their filter entries and modules.
- Dispatch helpers run filter callbacks for data out, data in processing, bind, listen, connect, accept, shutdown, name lookup, options, and ioctl.
- Deferred passive connections can be moved from the deferred accept list to the normal accept queue via `sof_newconn_ready()`, dropped after timeout, or moved between listeners for KSSL.
- Flow-control APIs let filters assert receive or send flow control; injection APIs let filters inject inbound or outbound mblks and report whether they became flow-controlled.
- `sof_bypass()` disables callbacks for an instance while leaving it attached.

## Integration Points
- Works with `sockparams.c` for socket-type matching and cleanup.
- Hooks into `sockcommon_sops.c` send/receive/control paths and `socknotify.c` notification events.
- Uses `sockconf_lock`, `so_fallback_rwlock`, `so_lock`, accept queue locks, kstats, taskq, and DTrace probes.
- Public filter callbacks and return values come from `sys/sockfilter.h`.

## Risks and Notes
- Filter attach paths must be nonblocking while holding `sockconf_lock` as writer.
- `SOFEF_CONDEMED` entries are freed only after active instance references drain.
- Deferred-close backlog is capped; if too large, new deferred drops are refused and counted in kstats.
- `sof_filter_data_in_proc()` can change receive queue length and must adjust `so_rcv_queued` while respecting flow-control semantics.
