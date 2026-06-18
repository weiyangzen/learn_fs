# File Research: sources/virtualization/libblockdev/src/utils/utils.h

Umbrella public header for libblockdev utility APIs used by the core library, plugins, and external consumers.

Key responsibilities:
- Includes the utility subheaders for size constants, process execution helpers, extra argument handling, device helpers, kernel module helpers, D-Bus helpers, and logging.
- Provides the GTK-Doc section block describing the utilities library and establishing `utils.h` as the public include.
- Uses a simple include guard `BD_UTILS`.

Dependencies and integration:
- Pulls in `sizes.h`, `exec.h`, `extra_arg.h`, `dev_utils.h`, `module.h`, `dbus.h`, and `logging.h`.
- Installed by `src/utils/Makefile.am` as `<blockdev/utils.h>`.
- Used by plugin code such as `src/plugins/check_deps.c` and `src/plugins/mdraid.h` to access shared utility APIs and size macros through a single include.
- Listed in package metadata and documentation as the main utility include.

Notable risks:
- Because this is an umbrella header, every consumer receives all included utility headers and their public macros; this increases namespace exposure, especially from `sizes.h`.
- Include-order changes here can affect downstream consumers that rely on transitive declarations from `<blockdev/utils.h>`.
