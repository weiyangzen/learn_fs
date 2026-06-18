# File Research: sources/virtualization/qemu/tools/qemu-vnc/qemu-vnc1.xml

## Purpose
D-Bus introspection XML for generated `org.qemu.Vnc1` bindings used by standalone `qemu-vnc`.

## Interfaces
### `org.qemu.Vnc1.Server`
Implemented at `/org/qemu/Vnc1/Server`.

Properties:
- `Name`
- `Auth`
- `VencryptSubAuth`
- `Clients`
- `Listeners`

Methods:
- `SetPassword`
- `ExpirePassword`
- `ReloadCertificates`
- `AddClient`

Signals:
- `ClientConnected`
- `ClientInitialized`
- `ClientDisconnected`
- `Leaving`

### `org.qemu.Vnc1.Client`
Implemented at `/org/qemu/Vnc1/Client_$id`.

Properties:
- `Host`
- `Service`
- `Family`
- `WebSocket`
- `X509Dname`
- `SaslUsername`

Signals:
- `ShutdownRequest`
- `ResetRequest`

## Integration
`tools/qemu-vnc/meson.build` runs `gdbus-codegen` on this XML to generate C bindings.

## Filesystem/Storage Relevance
None directly. It defines the management API for the virtualization VNC service.
