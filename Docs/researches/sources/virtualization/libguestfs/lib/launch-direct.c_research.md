# File Research: sources/virtualization/libguestfs/lib/launch-direct.c

Purpose: Implements the `direct` backend, launching qemu directly without libvirt and wiring it to the libguestfs appliance.

Key behavior:
- Backend private state stores qemu binary, qemu PID, recovery PID, and daemon socket path.
- Read-only drive overlays are created as qcow2 files using `guestfs_disk_create_argv`.
- Drive qemu arguments include file/source, snapshot/read-only behavior, cache mode, format, copy-on-read, discard, overlay handling, IDs, SCSI devices, serial labels, and block sizes.
- Picks a default qemu binary from `host_cpu`.
- Launch path verifies drives exist, builds/locates appliance, probes qemu/KVM, honors `force_tcg` and `force_kvm`, creates Unix daemon socket and optional console socketpair, then constructs qemu args before forking.
- Command line disables qemu defaults/user config, display, reboot, adds machine/CPU/memory/RTC/rng/virtio-scsi/drives/appliance/virtio-serial/console/channel/network/kernel/initrd/append args and custom hypervisor params.
- Networking uses `passt` when runnable, otherwise qemu user networking.
- Child process wires stdio/stderr to console socket unless direct mode is enabled, closes extra fds, optionally starts a process group, and execs qemu.
- Parent optionally forks a recovery process that kills qemu if the parent disappears.
- Launch waits for qemu to connect over virtio-serial, receives `GUESTFS_LAUNCH_FLAG`, checks handle state becomes `READY`, and adds a dummy appliance drive when needed.
- Cleanup kills qemu/recovery/passt as needed, closes sockets, frees qemuopts, clears connection, and resets state.
- Shutdown sends SIGTERM to qemu, kills recovery, waits, reports qemu failures, logs max RSS, and unlinks daemon socket.
- Registers backend ops for create overlay, default HV, launch, shutdown, get PID, and max disks.

Dependencies and state:
- Depends on qemuopts, command helpers, appliance builder, qemu/platform helpers, connection socket module, wait helpers, UEFI helpers, passt probing, launch progress, and backend registration.
- Mutates direct backend data, `g->conn`, `g->state`, `g->launch_t`, drive overlays/dummy appliance drive, and process state.

Risks:
- Process lifecycle is complex: multiple forks, recovery process polling, passt lifetime, socket ownership, and cleanup must stay aligned.
- qemu command construction is architecture- and version-sensitive.
- Force-KVM/TCG backend settings and KVM availability produce early launch failures.
