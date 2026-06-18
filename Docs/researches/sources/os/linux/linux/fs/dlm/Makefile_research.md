# File Research: sources/os/linux/linux/fs/dlm/Makefile

## Role

Build definition for the kernel Distributed Lock Manager.

## Behavior

Builds `dlm.o` when `CONFIG_DLM` is enabled.

Core object list includes:

- `ast.o`
- `config.o`
- `dir.o`
- `lock.o`
- `lockspace.o`
- `main.o`
- `member.o`
- `memory.o`
- `midcomms.o`
- `lowcomms.o`
- `plock.o`
- `rcom.o`
- `recover.o`
- `recoverd.o`
- `requestqueue.o`
- `user.o`
- `util.o`

When `CONFIG_DLM_DEBUG` is enabled, also includes `debug_fs.o`.

## Research Notes

The files in this group cover DLM callback delivery and configfs configuration, but the makefile shows they are part of a larger lock manager spanning networking, recovery, user ABI, and lockspace membership.
