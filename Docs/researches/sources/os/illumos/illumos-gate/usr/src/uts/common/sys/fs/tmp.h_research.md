# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/tmp.h

This header defines tmpfs per-mount state, memory limits, conversion macros, and internal operation declarations.

Mount state:
- `tmount` stores VFS pointer, root tmpnode, mount path, anonymous reservation limit, reserved anonymous pages, pseudo device number, generation number, contents lock, and per-mount rename lock.
- All fields are protected by `tm_contents`; renames are protected by `tm_renamelck`.

Conversions:
- `VFSTOTM`, `VTOTM`, `VTOTN`, and `TNTOV` map VFS/vnode/tmpnode state.
- `tmpnode_hold` and `tmpnode_rele` wrap vnode hold/release.

Directory operation enums:
- `de_op` distinguishes create, mkdir, link, and rename for directory enter.
- `dr_op` distinguishes remove, rmdir, and rename for directory remove.

Memory limits:
- `TMPMINFREE` defaults to 2 MiB and represents anonymous memory tmpfs leaves free for the rest of the system.
- `tmpfs_minfree` is exported in pages.
- `TMPMAXFRACKMEM` limits tmpfs kernel metadata memory to 1/25 of physical memory unless patched via `tmpfs_maxkmem`.
- `tmp_kmemspace` tracks metadata memory use.

Internal API:
- tmpnode init/truncate/growmap.
- Directory lookup/delete/init/truncate/enter.
- tmpfs memory allocate/free.
- anonymous memory reservation.
- access and sticky-remove checks.
- mount option number/mode conversion helpers.

Other:
- `TMP_MUSTHAVE` is a memory-allocation/reservation flag.

Dependencies and relationships:
- Tmpfs combines vnode/tmpnode metadata with anonymous memory reservation accounting.
- This header complements tmpnode definitions elsewhere by defining mount-level controls and internal helpers.
