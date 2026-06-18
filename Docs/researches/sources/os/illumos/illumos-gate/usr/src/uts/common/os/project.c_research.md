# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/project.c

## Purpose

`project.c` implements kernel project tracking and project-level resource controls. Projects group tasks/processes within zones, maintain usage counters, register resource controls, expose project kstats, and integrate with CPU caps, FSS, IPC, event ports, contracts, locked memory, crypto memory, and privilege daemon state.

Read completely: 1,162 lines.

## Main Responsibilities

- Maintains a global active-project dictionary keyed by `(project ID, zone ID)`.
- Reference-counts `kproject_t` objects and removes them when no task/thread/process references remain.
- Maintains a global circular project list for walking projects by zone.
- Initializes project-local accounting data and subsystem counters.
- Registers project resource controls at boot.
- Implements get/set/test usage callbacks for project CPU shares, CPU caps, LWPs, processes, tasks, SysV IPC IDs/memory, event ports, locked memory, contracts, and crypto memory.
- Creates and deletes per-project kstats for locked memory and process-count resource controls.
- Initializes the primordial project 0 and accounts the initial process/task/LWP.

## Important Data Structures And Globals

- `projects_hash`: mod_hash dictionary mapping `(projid, zoneid)` to `kproject_t`.
- `projects_list`: circular list of active projects.
- `project_hash_lock`: protects hash lookup, reference counts, and deletion.
- `projects_list_lock`: protects list traversal and link manipulation.
- `kproject_t`: project object containing IDs, zone, refcount, shares, counts, resource controls, CPU cap pointer, project data, kstats, and subsystem state.
- `kproject_data_t`: project subsystem usage counters for IPC, locked memory, contracts, crypto memory, and related kstats.
- `rc_project_*`: registered resource-control handles for every project-level rctl.

## Control Flow And Algorithms

`project_hold_by_id()` is the core lookup/create path. In find mode it looks up the project under the hash lock and increments the reference count if found. In insert mode it preallocates a `kproject_t`, resource-control set, and hash reservation; then under locks it either installs the new project, initializes default fields, derives rctls from project 0, inserts into the global list, notifies CPU caps, and creates kstats, or frees the spare if another thread won the race.

`project_rele()` decrements the reference count. When it reaches zero, it removes the project from the list, removes it from CPU caps, frees rctls, deletes kstats, frees any KLPD state, and destroys the hash entry, whose value destructor frees the `kproject_t`.

`project_walk_all()` walks the circular list from `proj0p`, optionally filtering by zone, and invokes a callback. `curprojid()` returns the current thread's project ID.

Resource-control callbacks follow a common pattern: usage functions read the current project counter, set functions update control/cache fields, and test functions compare `usage + increment` against the proposed rctl value while required locks are held.

`project_init()` creates the hash, registers all built-in project resource controls, installs default and legacy limits, computes memory-based defaults for crypto/shared memory, creates project 0, and seeds its counts from `p0`/`t0`.

Kstat helpers allocate virtual named kstats with `zonename`, `usage`, and `value` fields; update functions report locked memory or process-count usage and configured limit.

## Dependencies And Integration

- Uses `mod_hash` for project lookup and `rctl` for resource-control registration/state.
- Integrates with zones, tasks, processes, FSS CPU shares, CPU caps, SysV IPC, event ports, contracts, kernel crypto, locked memory accounting, kstats, and KLPD.
- Many counters are shared with zone locks such as `zone_nlwps_lock` and `zone_mem_lock`.

## Locking And Concurrency

The documented order is hash lock before list lock when both are needed. Project list walking requires `projects_list_lock`. Reference count changes require `project_hash_lock`. Several usage/test paths assert `p_lock` plus subsystem-specific zone locks. Creation preallocates before acquiring contended locks to allow `KM_SLEEP` allocations safely.

## Notable Risks And Invariants

- The hash dictionary entry does not count as an external reference; only tasks/threads/processes and explicit holds do.
- Project deletion asserts no remaining process count and no CPU cap pointer.
- Project keys include zone ID, so identical project IDs in different zones are distinct.
- New projects inherit resource controls from project 0.
- Resource-control callbacks assume callers hold the locks asserted in each callback.

## Research Relevance

Projects are a major illumos workload accounting and limit boundary. Filesystem/storage behavior can be affected by project rctls for process count, locked memory, IPC resources, CPU shares/caps, and event-port IDs, so this file is important for workload isolation research.
