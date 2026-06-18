# File Research: sources/os/bsd/freebsd-src/sys/sys/module_khelp.h

Defines kernel helper module declaration structures and macros.

Key content:
- Helper flag `HELPER_NEEDS_OSD`.
- `struct helper` contains init/destroy callbacks, fixed-size name, UMA zone, hook info pointer/count, classes, id, refcount, flags, and list linkage.
- `struct khelp_modevent_data` carries helper module declaration data: name, helper object, hooks, hook count, UMA zone size, constructor, and destructor.
- `KHELP_DECLARE_MOD_UMA` builds modevent data, moduledata, declares the module at `SI_SUB_KHELP`, and records module version.
- `KHELP_DECLARE_MOD` is the no-UMA convenience wrapper.
- Declares `khelp_modevent`.

Research relevance:
- Provides module scaffolding for kernel helper frameworks with hooks and optional UMA per-object storage.
- Depends on `module.h` module declaration/version mechanisms and UMA types.

Cautions:
- Helper names are limited to 16 bytes including terminator constraints in fixed buffers.
- Hook structures are referenced but not defined here.
