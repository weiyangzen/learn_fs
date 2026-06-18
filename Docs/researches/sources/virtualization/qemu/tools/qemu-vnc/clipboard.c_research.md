# File Research: sources/virtualization/qemu/tools/qemu-vnc/clipboard.c

## Purpose
Bridges QEMU’s internal clipboard peer API with QEMU’s D-Bus display clipboard interface for standalone `qemu-vnc`.

## Behavior
- Supports UTF-8 text clipboard only: `text/plain;charset=utf-8`.
- Maintains D-Bus clipboard proxy/skeleton and one pending request per selection.
- On local clipboard update, advertises/grabs text MIME availability over D-Bus.
- On remote grab, creates a `QemuClipboardInfo` and updates QEMU clipboard state if serial is valid.
- On remote release, releases the corresponding clipboard peer selection.
- On request, returns existing clipboard data or triggers an async local request with a five-second timeout.
- On unregister, cancels pending requests.
- Registers as a `QemuClipboardPeer` named `dbus`.

## Error Handling
Rejects invalid selections, concurrent pending requests, empty clipboard, and unsupported MIME requests with D-Bus errors.

## Filesystem/Storage Relevance
None directly. It is desktop/console integration for the virtualization UI path.
