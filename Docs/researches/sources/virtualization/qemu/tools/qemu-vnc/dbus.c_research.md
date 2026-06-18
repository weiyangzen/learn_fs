# File Research: sources/virtualization/qemu/tools/qemu-vnc/dbus.c

## Purpose
Implements the standalone `qemu-vnc` management D-Bus API under `org.qemu.Vnc1`, and forwards QEMU VNC client events into D-Bus objects/signals.

## Main Structures
- `VncDbusClient`: one D-Bus object per connected VNC client, with host/service/path/auth metadata.
- Global server skeleton and object manager for `/org/qemu/Vnc1`.

## Server API Behavior
- Exports `/org/qemu/Vnc1/Server`.
- Sets server properties: name, auth, vencrypt subauth, clients, and listeners.
- Implements methods:
  - `SetPassword`
  - `ExpirePassword`
  - `ReloadCertificates`
  - `AddClient`
- Builds listener property data from `qmp_query_vnc_servers()`.

## Client Tracking
- On connect, creates `/org/qemu/Vnc1/Client_<id>`, sets host/service/family/websocket, updates server `Clients`, and emits `ClientConnected`.
- On initialized, fills X.509 DN and SASL username where available and emits `ClientInitialized`.
- On disconnect, emits `ClientDisconnected`, unexports the object, removes it from the list, and updates `Clients`.

## Event Forwarding
Overrides local `qapi_event_emit()` for VNC connected/initialized/disconnected events and maps the QDict event payload into D-Bus client updates.

## VNC Actions
`vnc_action_shutdown()` and `vnc_action_reset()` locate the D-Bus client for a `VncState` and emit corresponding client signals.

## Filesystem/Storage Relevance
None directly. It is management/control-plane infrastructure for the standalone virtualization UI tool.
