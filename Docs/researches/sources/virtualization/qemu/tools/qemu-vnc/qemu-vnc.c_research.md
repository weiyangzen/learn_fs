# File Research: sources/virtualization/qemu/tools/qemu-vnc/qemu-vnc.c

## Purpose
Main program for standalone `qemu-vnc`, a VNC server that connects to a running QEMU instance through the `org.qemu.Display1` D-Bus display interface.

## Main State
`QemuVncState` tracks D-Bus connection/name, selected chardev names, shutdown reason, VT enabling, owner tracking, and termination flags.

## Startup Flow
- Initializes QEMU exec/data dirs, trace, QOM, options, and main loop.
- Parses GLib options for D-Bus address or p2p fd, bus name, wait mode, VNC listen address, websocket, sharing, TLS, SASL, objects, chardev exposure, keyboard layout, password, lossy mode, and adaptive encoding.
- Creates optional user-creatable objects.
- Creates TLS credentials and optional systemd credential-backed VNC password secret.
- Converts CLI settings into a QEMU `vnc` option with id `default`.
- Connects to session bus, custom bus address, or p2p fd.
- Watches the QEMU bus name or starts setup immediately for p2p/direct connection.

## Display Setup
- Optionally reads VM name from `/org/qemu/Display1/VM`.
- Creates a D-Bus object manager for display objects.
- Discovers console object paths and sorts them for deterministic console numbering.
- Calls `console_setup()` for each console.
- Creates the VNC display after consoles exist.
- Initializes VNC management D-Bus API, clipboard, audio, and optional chardev text consoles.

## Shutdown
Terminates when the D-Bus owner vanishes, connection closes, or setup fails; emits a VNC D-Bus `Leaving` signal, cleans up VNC D-Bus state and VNC display state, and exits.

## Filesystem/Storage Relevance
None directly. This is standalone virtualization UI entrypoint code.
