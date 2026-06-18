# File Research: sources/os/plan9/9front/sys/src/cmd/1l/compat.c

Small compatibility wrapper for the `1l` linker.

Key contents:
- Includes `l.h`.
- Includes the shared `../cc/compat` implementation body.

Role in system:
- Pulls shared Plan 9 compiler-tool compatibility helpers into the linker build without duplicating their source.
