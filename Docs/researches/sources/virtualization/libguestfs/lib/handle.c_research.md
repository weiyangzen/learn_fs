# File Research: sources/virtualization/libguestfs/lib/handle.c

Purpose: Creates, configures, shuts down, and destroys `guestfs_h` handles, and implements many generated getter/setter APIs.

Key behavior:
- Constructor initializes libvirt and libxml2 for multithreaded use.
- `guestfs_create_flags` allocates a handle, initializes recursive locks, TLS key, defaults, backend, program name, environment-derived settings, and optional close-on-exit registration.
- Environment parsing supports debug/trace, tmp/cache/runtime dirs, appliance path, hypervisor, append args, memsize, backend, and backend settings.
- `guestfs_close` removes the handle from the global list, emits trace/close events, shuts down if needed, frees temp dirs, FUSE state, drives, backend data, private data, strings, error TLS records, and the handle itself.
- `shutdown_backend` autosyncs when ready, invokes backend shutdown, frees connection/drives/features, and resets state to `CONFIG`.
- Implements setters/getters for verbose, autosync, path, qemu/hv, append, memsize, SELinux, version, trace, direct mode, recovery process, network, program, identifier, backend, attach method compatibility, backend settings, process group, and SMP.
- Backend settings support `name`, `name=value`, clear, get, set, and boolean lookup with suppressed “not found” errors.

Dependencies and state:
- Uses global handle list protected by `handles_lock`, per-handle lock from generated wrappers, libxml2, optional libvirt, hash private data, tempdir/drives/FUSE cleanup, backend ops, and error/event subsystems.
- Mutates most configuration fields in `guestfs_h`.

Risks:
- Double close is detected only by `g->state == NO_HANDLE`; using a freed handle remains undefined outside this guard.
- `guestfs_impl_get_hv` cannot report a backend default before backend data exists after launch.
- Environment parsing has many legacy aliases, so behavior changes can affect compatibility.
