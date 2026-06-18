# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/sockfs/sockparams.c

## Purpose
Manages sockfs socket-parameter records that map socket family/type/protocol tuples to socket modules and optional STREAMS devices.

## Main Behavior
- Initializes global configured sockparams and ephemeral sockparams lists plus global ephemeral allocation/reuse kstats.
- `sockparams_create()` builds a `sockparams` entry, initializes automatic/programmatic filter lists and per-entry kstats, validates module/device inputs, and opens STREAMS device vnodes when needed.
- `sockparams_destroy()` releases device vnodes, module references, kstats, filters, locks, and memory.
- Ephemeral sockparams are reused or created for caller-specified modules/devices and TPI fallback; the last reference removes them from the ephemeral list and destroys them.
- `sockparams_add()` inserts configured entries after kstat setup and filter initialization.
- `sockparams_delete()` removes unused configured entries or returns `EBUSY`.
- `solookup()` finds exact socket tuple entries, reports precedence-aware errors for unsupported family/protocol/type, lazily loads socket modules, and returns held entries.
- Filter cleanup/addition helpers remove or add filter references across configured and ephemeral sockparams.
- `sockparams_copyout_socktable()` copies the configured socket table to userland, including tuple, module name, device path, refcount, and flags.

## Integration Points
- Used by `socket_create()`, TPI fallback, socket configuration ioctls, socket filters, and module registration.
- Coordinates with `smod_lookup_byname()`, `SMOD_DEC_REF`, `sof_sockparams_init()`, `sof_sockparams_fini()`, and `sockconf_lock`.

## Risks and Notes
- Lock order is documented as `sockconf_lock -> sp_lock`.
- `solookup()` holds entries before dropping `sockconf_lock` for module loading so entries cannot disappear mid-load.
- Ephemeral entries are not placed on the global configured list and disappear when their refcount reaches zero.
- `sockparams_copyout_socktable()` can return `EAGAIN` if the configured table grows beyond the user-provided entry count while copying.
