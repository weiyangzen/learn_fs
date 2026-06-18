## sources/test-tools/fio/cgroup.c

Purpose: creates, joins, and cleans fio per-job blkio cgroups when cgroup support is compiled in. It supports legacy cgroup v1 blkio mounts and unified cgroup v2 mounts.

Important APIs and flow: `find_cgroup_mnt()` scans `/proc/mounts` with `getmntent_r()` for a cgroup mount carrying `blkio` options or for a `cgroup2` mount. `cgroup_setup()` lazily finds the mount, builds the job cgroup path from `td->o.cgroup` or job name, creates the directory, records newly created cgroups in a shared list, optionally writes `blkio.weight` for v1, and moves `td->pid` into `tasks` or `cgroup.procs`. `cgroup_shutdown()` moves the pid back to the root cgroup and frees the mount record. `cgroup_kill()` removes tracked cgroup directories unless `cgroup_nodelete` was set.

State and persistence: state lives in a process-global semaphore `lock`, a caller-owned `flist_head` of `struct cgroup_member`, and filesystem directories/files under the mounted cgroup hierarchy. Constructor/destructor functions initialize and remove the semaphore.

Dependencies and integration: uses `fio.h`, `flist`, `smalloc`, `td_verror()`, and Linux mount/cgroup filesystem conventions. It integrates with job setup/shutdown code through `cgroup_setup()` and `cgroup_shutdown()`.

Risks and test signals: behavior depends on process permissions and cgroup mount shape. cgroup v2 rejects `cgroup_weight` with an error, and there is a typo in that error text. Path construction validates overflow, but filesystem races and pre-existing directories affect cleanup ownership. Test signals require Linux cgroup environments; failures surface through `td_verror()` and log messages.
