# File Research: sources/virtualization/qemu/tools/qemu-vnc/input.c

## Purpose
Forwards QEMU/VNC input events to QEMU’s D-Bus display keyboard and mouse interfaces.

## Behavior
- Maintains LED event handlers and mouse mode notifiers expected by QEMU UI code.
- Converts Linux keycodes to QEMU key numbers and sends D-Bus `Press`/`Release`.
- Queues absolute and relative mouse motion until `qemu_input_event_sync()`.
- Sends absolute position or relative motion D-Bus calls on sync.
- Reports absolute mouse capability from D-Bus mouse property.
- Sends mouse button press/release calls for changed button bits.
- Reacts to keyboard modifier and mouse absolute-mode property changes.

## Filesystem/Storage Relevance
None directly. It is virtualization UI input integration.
