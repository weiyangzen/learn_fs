# File Research: sources/os/linux/linux/fs/pstore/Makefile

## Role

Build rules for the pstore subsystem.

## Contents

- Builds `pstore.o` from `inode.o` and `platform.o` under `CONFIG_PSTORE`.
- Adds `ftrace.o` and `pmsg.o` conditionally for their frontends.
- Builds `ramoops.o` from `ram.o` and `ram_core.o`.
- Builds `pstore_zone.o` from `zone.o`.
- Builds `pstore_blk.o` from `blk.o`.

## Research Notes

The Makefile mirrors the architectural split: common pstore core, optional frontends, RAM backend, zone manager, and block backend.
