# File Research: sources/virtualization/libguestfs/lib/appliance.c

## Role
Locates or builds the libguestfs appliance used to run the daemon VM.

## Appliance Search Order
- Search each element of `g->path`.
- Prefer supermin appliance skeletons under `supermin.d`.
- If found, build/cache a full appliance with `supermin --build`.
- Otherwise accept a fixed appliance containing `README.fixed`, `kernel`, `initrd`, and `root`.
- Otherwise accept old-style appliance files `vmlinuz.<host_cpu>` and `initramfs.<host_cpu>.img`.

## Supermin Build
- Uses `$TMPDIR/.guestfs-$UID/appliance.d` and a lock file.
- Runs `supermin --build --if-newer --lock --copy-kernel -f ext2 --host-cpu <host_cpu>`.
- Touches built kernel/initrd/root files so temp cleanup policies do not remove active cache entries.

## Error Handling
If no path element matches, reports that no suitable supermin, fixed, or old-style appliance was found on `LIBGUESTFS_PATH`.

## Filesystem/Storage Relevance
This file creates or locates the miniature Linux environment that performs all guest filesystem and block operations.
