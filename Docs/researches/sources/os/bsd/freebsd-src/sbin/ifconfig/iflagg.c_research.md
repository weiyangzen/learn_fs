# File Research: sources/os/bsd/freebsd-src/sbin/ifconfig/iflagg.c

`iflagg.c` implements ifconfig support for link aggregation interfaces. It registers clone-time `laggtype`, runtime port/protocol/hash/options commands, status printing, and a `lagg` clone callback.

The command handlers manage ports (`SIOCSLAGGPORT`, `SIOCSLAGGDELPORT`), aggregation protocol (`SIOCSLAGG`), flowid shift and round-robin limit (`SIOCSLAGGOPTS`), boolean lagg options, and hash selection (`SIOCSLAGGHASH`). Protocol/type names are resolved from kernel-provided macro tables such as `LAGG_PROTOS` and `LAGG_TYPES`.

`lagg_status()` uses `ifconfig_lagg_get_lagg_status()` from libifconfig, prints protocol and hash fields, optionally prints lagg options/statistics in verbose mode, then prints every member port and LACP state/peer details where applicable.

The file includes helpers for formatting LACP actor/partner identifiers and MAC addresses. `lagg_create()` passes accumulated `struct iflaggparam params` to `ifcreate_ioctl()`.

Notable edge behavior: adding a failed/missing port warns and sets global `exit_code = 1` but does not immediately terminate, with a comment explaining this avoids taking down an entire lagg due to one failed NIC. Existing ports are ignored via `EEXIST`.
