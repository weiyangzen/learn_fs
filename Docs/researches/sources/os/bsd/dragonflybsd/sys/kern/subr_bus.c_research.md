# File Research: sources/os/bsd/dragonflybsd/sys/kern/subr_bus.c

DragonFly BSD kernel bus/device framework core. It manages devclasses, devices, driver module registration, generic bus methods, resource hints, root bus bootstrapping, and user-visible device-tree reporting.

Key responsibilities:
- Creates `hw.bus` and `dev.*` sysctl surfaces for bus generation, device metadata, devclass parents, device descriptions, drivers, PNP info, locations, and parents.
- Implements `/dev/devctl` as a single-reader event queue with blocking/nonblocking reads, kqueue read readiness, optional `SIGIO`, and formatted add/remove/no-match notifications.
- Maintains global devclass and device lists, unit allocation, device naming, parent/child links, device state transitions, softc allocation, descriptions, sysctl lifecycle, and bus data generation changes.
- Probes drivers by devclass and parent devclass inheritance, supports global driver priority filtering, handles attach/detach/shutdown/suspend/resume, and optionally launches asynchronous attach threads.
- Implements root bus creation/configuration and dynamic driver module load/unload handling.
- Provides runtime/config-time resource hint lookup and mutation plus `resource_list_*` helpers.
- Provides generic bus method implementations that propagate interrupts, resources, ivars, DMA tags, and child operations up the bus hierarchy.

Important behavior:
- `root_bus_configure()` identifies/probes root children and waits for async attaches before marking the root bus attached.
- Driver load calls `BUS_DRIVER_ADDED()` on already attached busses so newly loaded modules can bind existing devices.
- Failed probes emit no-match notifications once per device through `DF_DONENOMATCH`.
- Device detach refuses busy devices, tears down sysctls, clears non-fixed devclasses, and resets the driver/kobj binding.
- `hw.bus.devices` is generation-checked; userland must retry if the bus generation changes.

Dependencies:
- Depends on DragonFly `kobj`, module, sysctl, devfs/dev_ops, rman/resource, bus method macros, lwkt threads, locks, caps, signal, and interrupt APIs.
- Interacts with config-generated `config_devtab` and kernel environment hints in both DragonFly and FreeBSD naming forms.

Notable risks:
- Much of the device/devclass global state is manipulated without a single visible global lock in this file; callers rely on bus configuration ordering and subsystem conventions.
- `/dev/devctl` intentionally supports only one reader and can drop events on allocation failure.
- `devaddq()` has suspicious cleanup logic: if `loc` allocation fails after `data` allocation, the `bad:` path does not free `data` because it checks `loc` before freeing `data`.
- Resource hint generic matching has an in-code XXX noting that the generic pass still compares `devtab[i].unit == unit`, which makes generic unit entries questionable.
