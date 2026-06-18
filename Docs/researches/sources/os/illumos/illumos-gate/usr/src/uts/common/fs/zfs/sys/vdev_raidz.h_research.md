# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/vdev_raidz.h

This public header declares RAID-Z map and math-selection interfaces.

Public API surface:
- `vdev_raidz_map_alloc()` and `vdev_raidz_map_free()` allocate/free a `raidz_map` for a zio and geometry.
- `vdev_raidz_generate_parity()` generates parity columns.
- `vdev_raidz_reconstruct()` reconstructs missing data/parity targets.
- Math subsystem lifecycle and dispatch: `vdev_raidz_math_init()`, `vdev_raidz_math_fini()`, `vdev_raidz_math_get_ops()`, `vdev_raidz_math_generate()`, `vdev_raidz_math_reconstruct()`, and `vdev_raidz_impl_set()`.

Risk-sensitive invariants:
- The public interface is intentionally opaque; detailed map geometry and implementation operations are in `vdev_raidz_impl.h`.
- Userland builds define a dummy `kernel_param` for shared code compatibility.
