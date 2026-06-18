# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dc_ki.h

Kernel interface header for Sun Cluster bootstrap integration. It declares hooks used by drivers/modules loaded before the root filesystem is mounted.

Key elements:
- Includes types, DDI, and module-control definitions.
- Declares `cluster()` plus `clboot_modload()`, `clboot_loadrootmodules()`, `clboot_rootconf()`, and `clboot_mountroot()`.
- Comments state the routines are implemented in the `misc/cl_bootstrap` module from the SunCluster consolidation.

Dependencies:
- Depends on `struct modctl`, DDI declarations, and early boot/root-mount code that calls these hooks.

Research notes:
- This is a narrow external integration point; the header contains declarations only and no local state.
- The functions sit on the boot path before root is mounted, so callers cannot assume normal filesystem/module availability.
