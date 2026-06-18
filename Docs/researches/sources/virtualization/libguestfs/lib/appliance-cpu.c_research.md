# File Research: sources/virtualization/libguestfs/lib/appliance-cpu.c

## Role
Selects the CPU model string used to boot the libguestfs appliance under qemu/libvirt.

## Main Logic
- On aarch64, returns `host` for KVM and `cortex-a57` for TCG because qemu’s default `virt` machine CPU is unsuitable.
- On powerpc64 and loongarch64, returns `NULL` to avoid problematic CPU options.
- On most other architectures, returns `max`.

## Filesystem/Storage Relevance
The selected CPU model affects whether the appliance boots reliably and efficiently, which gates all filesystem operations.
