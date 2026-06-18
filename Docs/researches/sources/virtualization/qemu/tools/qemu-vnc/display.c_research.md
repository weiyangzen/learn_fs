# File Research: sources/virtualization/qemu/tools/qemu-vnc/display.c

## Purpose
D-Bus display listener for standalone `qemu-vnc`, handling graphic console scanout, incremental updates, shared-memory scanout, cursor updates, UI info, and input proxy discovery.

## Main Structure
`ConsoleData` stores D-Bus console/keyboard/mouse proxies, the local graphic console, listener connection, and whether the current surface is read-only.

## Behavior
- Creates proxies for `org.qemu.Display1.Console`, `Keyboard`, and `Mouse`.
- Creates a local QEMU graphic console.
- Registers a D-Bus display listener through a peer-to-peer socket connection.
- Implements listener methods:
  - `Scanout`: creates writable pixman surface from D-Bus byte array.
  - `Update`: composites update pixels into active writable surface.
  - `ScanoutMap`: mmaps passed fd read-only with `MAP_PRIVATE` and creates surface.
  - `UpdateMap`: marks rectangle dirty for mapped scanout.
  - `CursorDefine`: creates and installs QEMU cursor.
- Sends UI size information back through `SetUIInfo`.
- Calls `input_setup()` with keyboard and mouse proxies.

## Safety/Ownership
- Byte-array scanout keeps the `GVariant` alive until pixman image destroy.
- Mapped scanout unmaps memory through pixman destroy callback.
- Plain updates are rejected when the active surface is read-only.

## Filesystem/Storage Relevance
None directly. It is display plumbing for virtualization UI.
