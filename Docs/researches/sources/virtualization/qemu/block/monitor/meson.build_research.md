# File Research: sources/virtualization/qemu/block/monitor/meson.build

## Purpose
Adds the block monitor command sources to the appropriate QEMU Meson source sets.

## Main Entry Points
- `system_ss.add(files('block-hmp-cmds.c'))` builds HMP block monitor commands into the system emulator source set.
- `block_ss.add(files('bitmap-qmp-cmds.c'))` builds dirty bitmap QMP command helpers into the block source set.

## Internal Mechanics
This is a two-line build manifest with no conditional logic. It separates HMP system-emulator monitor code from block-layer QMP bitmap command code.

## Dependencies
Depends on QEMU’s Meson source-set variables `system_ss` and `block_ss`.

## Risks and Notes
The split is intentional: HMP commands are system-emulator-facing, while bitmap QMP helpers belong with block code and can be shared by block command infrastructure.
