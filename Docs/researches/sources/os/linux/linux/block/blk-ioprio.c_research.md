# File Research: sources/os/linux/linux/block/blk-ioprio.c

## Summary
Implements a blkcg policy that assigns or constrains bio I/O priority class based on cgroup configuration.

## Main Responsibilities
- Register cgroup files for I/O priority policy.
- Store per-cgroup priority policy.
- Apply policy to each bio before request scheduling.
- Support both cgroup v1 legacy and cgroup v2 default file exposure.

## Key APIs
- `blkcg_set_ioprio()`.
- cgroup file `prio.class`.
- Policy lifecycle: `ioprio_init()`, `ioprio_exit()`.

## Important Behavior
Supported policies are `no-change`, `promote-to-rt`, `restrict-to-be`, `idle`, and `none-to-rt`. `none-to-rt` is treated as an alias for promotion to realtime.

Promotion changes non-RT bios to `IOPRIO_CLASS_RT` with priority level 4. Restriction and idle use `max_t()` over encoded `bi_ioprio`, relying on Linux I/O priority encoding where higher numeric values usually mean lower priority except for `IOPRIO_CLASS_NONE`.

## State and Synchronization
Per-cgroup state is a small `struct ioprio_blkcg` allocated as blkcg policy data. Writes replace the enum policy value directly from kernfs context.

## Risks
Policy behavior depends on encoded I/O priority ordering. This policy affects writeback I/O associated with cgroups, unlike task-only `ioprio_set()`, so cgroup placement directly changes background filesystem writeback priority.
