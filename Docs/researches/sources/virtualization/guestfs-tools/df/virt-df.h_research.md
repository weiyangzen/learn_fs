# File Research: sources/virtualization/guestfs-tools/df/virt-df.h

## Scope

Shared header for `virt-df`.

## APIs And Globals

- Declares output mode globals: `csv`, `human`, `inodes`, and `uuid`.
- Declares `df_on_handle`.
- Declares libvirt worker `df_work` when `HAVE_LIBVIRT`.
- Declares output functions `print_title` and `print_stat`.

## Risks And Invariants

- Shared globals are set by `main.c` and consumed by `output.c`.
- Header assumes `guestfs_h` and `guestfs_statvfs` are visible through included libguestfs headers in implementation files.
