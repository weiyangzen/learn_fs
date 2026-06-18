# File Research: sources/os/bsd/freebsd-src/sbin/nvmecontrol/modules/Makefile.inc

Common Makefile settings for `nvmecontrol` vendor modules.

Key contents:
- Package: `nvme-tools`.
- Sets `NVMECONTROLDIR`.
- Disables install library metadata with `MK_INSTALLLIB=no`.
- Adds include path to the main `nvmecontrol` directory.
- Default shared library name is `${LIB}.so`.
- Installs modules under `/lib/nvmecontrol`.

Research notes:
- Shared modules rely on symbols exported by the main binary, matching `nvmecontrol/Makefile` use of `-rdynamic`.
