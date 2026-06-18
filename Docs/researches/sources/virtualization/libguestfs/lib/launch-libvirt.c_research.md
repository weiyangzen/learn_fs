# File Research: sources/virtualization/libguestfs/lib/launch-libvirt.c

Libvirt backend implementation for launching the libguestfs appliance as a transient libvirt domain.

Important behavior:
- Registers the `libvirt` backend through `guestfs_int_init_libvirt_backend`.
- `launch_libvirt` selects `qemu:///session` for non-root and `qemu:///system` for root unless a backend URI is supplied.
- Reads libvirt capabilities and domain capabilities to choose qemu vs KVM, default emulator path, and firmware autoselection support.
- Builds or locates the appliance, creates qcow2 overlays for the appliance and read-only drives, and creates Unix sockets for guestfsd and console communication.
- Constructs complete libvirt domain XML with memory, CPU model, ACPI/timers, kernel/initrd/cmdline, optional UEFI loader/nvram, sVirt labels, virtio-scsi disks, console/channel sockets, optional passt networking, and qemu command-line extras.
- Handles file, block, network, and overlay disks; rejects qemu curl protocols for libvirt with a direct-backend suggestion.
- Uses libvirt secrets for authenticated network disks, including base64 decode for RBD secrets and protocol-specific secret types.
- Launches with `virDomainCreateXML(..., VIR_DOMAIN_START_AUTODESTROY)`, accepts console/daemon connections, waits for `GUESTFS_LAUNCH_FLAG`, then marks the appliance ready through protocol handling.
- `shutdown_libvirt` destroys and frees the domain/connection, unlinks sockets, frees labels, secrets, UEFI state, and capability-derived strings.
- `destroy_domain` retries indefinitely on libvirt `EBUSY`, ignores missing-domain errors, and can request graceful destruction.

Filesystem relevance:
- This is the main libvirt path for attaching guest disks safely to the appliance, including copy-on-write overlays for read-only access, discard settings, block sizes, disk labels, and network-backed storage.
