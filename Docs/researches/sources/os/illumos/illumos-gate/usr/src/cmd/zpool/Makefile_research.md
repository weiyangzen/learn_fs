# File Research: sources/os/illumos/illumos-gate/usr/src/cmd/zpool/Makefile

This makefile builds the illumos `zpool` command-line frontend.

Build targets and objects:
- Produces `zpool`.
- Compiles `zpool_main.o`, `zpool_vdev.o`, `zpool_iter.o`, and `zpool_util.o`.
- Derives source, catalog fragment, and clean-file lists from the object list.
- Builds `zpool.po` by concatenating per-object `.po` files.

Install behavior:
- Installs the real program under `/sbin` through the standard command makefile.
- Creates `/usr/sbin/zpool` as a symlink back to `/sbin/zpool`.

Dependencies:
- Links against `libzfs`, `libnvpair`, `libdevid`, `libefi`, `libdiskmgt`, `libuutil`, `libumem`, `libzutil`, `libm`, and `libzpool`.
- Includes common ZFS headers, kernel ZFS headers, and libzutil common headers.
- Includes `../stat/Makefile.stat`, indicating shared iostat/stat support with the `stat` command infrastructure.

Build configuration:
- Includes `Makefile.cmd`, `Makefile.cmd.64`, and `Makefile.ctf`.
- Uses GNU99 C mode.
- Defines `DEBUG` for non-release builds.

Risk notes:
- `zpool_iter.c` and pool/vdev command code depend on libuutil AVL/list support and nvlist layout from libzfs/libzpool.
- Link dependencies include disk, EFI, devid, and zpool internals; removing libraries can break subcommands outside this small file group.
- The `/usr/sbin` symlink is part of the expected administrative command path.
