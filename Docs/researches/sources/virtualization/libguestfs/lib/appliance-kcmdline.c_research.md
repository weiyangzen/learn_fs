# File Research: sources/virtualization/libguestfs/lib/appliance-kcmdline.c

## Role
Builds the Linux kernel command line for the libguestfs appliance.

## Root UUID Handling
- `get_root_uuid_with_file()` reads ext filesystem magic and UUID directly from a raw appliance image.
- It skips direct ext-superblock probing for qcow2 magic.
- `run_qemu_img_dd()` uses `qemu-img dd` to extract the first 256 KiB of qcow2-like images into a raw temp file.
- `get_root_uuid()` combines both paths and returns the appliance root UUID.

## Command Line Construction
`guestfs_int_appliance_command_line()` builds a space-joined argument list containing panic behavior, architecture console settings, boot workarounds, udev timeouts, TCG `lpj`, logging controls, cgroup/USB/crypto optimizations, root UUID, SELinux mode, verbosity, network enablement, sanitized `TERM`, handle identifier, and user append string.

## Architecture Handling
Defines serial console and early printk settings per architecture, including aarch64-specific EFI RTC suppression and log verbosity.

## Filesystem/Storage Relevance
This file determines how the appliance locates and mounts its root filesystem and how it boots into a state capable of serving guest filesystem requests.
