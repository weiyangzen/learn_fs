# File Research: sources/virtualization/qemu/tools/qemu-vnc/meson.build

## Purpose
Meson build definition for the standalone `qemu-vnc` executable and generated D-Bus bindings.

## Behavior
- Applies VNC source set `vnc_ss`.
- Generates `qemu-vnc1.h` and `qemu-vnc1.c` from `qemu-vnc1.xml` using `gdbus-codegen`.
- Builds executable `qemu-vnc` from:
  - main/source bridge files
  - VNC source set output
  - generated D-Bus display and VNC1 bindings
- Links dependencies: VNC dependencies, `io`, `crypto`, `qemuutil`, `gio`, and `ui`.
- Creates a development symlink from build subdir to `../../qemu-bundle` so relocated path lookup works.

## Filesystem/Storage Relevance
None directly. It controls build integration for the standalone virtualization UI tool.
