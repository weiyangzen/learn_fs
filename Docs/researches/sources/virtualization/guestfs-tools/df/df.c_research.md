# File Research: sources/virtualization/guestfs-tools/df/df.c

## Scope

Core filesystem stat collection for `virt-df`.

## Behavior

- `df_on_handle` lists devices and filesystems from an already launched guestfs handle.
- Skips empty, swap, and unknown filesystem types.
- For each candidate filesystem, suppresses libguestfs errors, attempts read-only mount at `/`, calls `statvfs`, unmounts all, then prints stats if successful.
- Avoids exiting on individual guestfs failures to stay robust against bad guests.
- Under libvirt, `df_work` adds domain disks read-only, launches the handle, and delegates to `df_on_handle`.

## Dependencies And Risks

- Read-only mount failures are expected and silently ignored.
- `df_work` traditionally ignores errors adding libvirt disks but treats launch failures as errors.
