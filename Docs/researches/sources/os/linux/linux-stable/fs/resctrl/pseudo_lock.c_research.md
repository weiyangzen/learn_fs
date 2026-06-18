# File Research: sources/os/linux/linux-stable/fs/resctrl/pseudo_lock.c

Implements cache pseudo-locking support for resctrl control groups.

Key responsibilities:
- Converts an eligible empty control group into pseudo-lock setup mode, then into a pseudo-locked cache-resident memory region after a valid schemata write.
- Allocates and initializes `struct pseudo_lock_region`, computes region size from CBM/cache metadata, allocates backing kernel memory, and runs architecture pseudo-locking code on a CPU in the target cache domain.
- Prevents unsafe setup when the group is default, CDP is enabled, prefetch-disable support is absent, monitoring is active, tasks are assigned, or CPUs are assigned.
- Restricts/restores user access to `tasks`, `cpus`, `cpus_list`, and `mon_groups` during setup.
- Tracks pseudo-lock device minors and exposes each completed region as `/dev/pseudo_lock/<group>`.
- Creates optional debugfs measurement trigger for latency and cache residency measurements.
- Enforces mapping constraints in the character-device mmap path: target domain must still exist, current task affinity must be subset of the pseudo-locked domain CPUs, mapping must be shared, and bounds must fit the region.

Important cleanup:
- Removal relaxes PM QoS C-state constraints, removes debugfs files, destroys the device, releases the minor, frees the region, and frees CLOSID/RMID state as appropriate.
- Domain overlap helpers prevent new CBMs from overlapping existing pseudo-locked cache portions or cache hierarchy conflicts.

Notable invariants:
- Pseudo-lock setup frees the group RMID because monitoring is not allowed.
- Completed pseudo-locked groups free their CLOSID because no tasks/CPUs use that CLOSID afterward.
- mmap is deliberately non-seekable and does not allow private copy-on-write mappings.
