# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/dvx-head.mak

Purpose: Shared DesqView/X makefile header included before the generic Ghostscript makefiles.

Key definitions:
- Sets `PLATFORM=dvx_`.
- Defines command/object/executable suffix conventions: `.bat`, `.o`, `.exe`.
- Defines make syntax helpers for `-D`, `-I`, output switches, quoting, and no-op commands.
- Defines DOS/DesqView/X command flavor: `CAT=type`, path separator `D=\\`, empty shell variables.
- Sets generic file commands `CP_=cp`, `RM_=rm -f`.
- Sets `genconf` arguments: `CONFILES=-p -pl &-l%%s`, `CONFLDTR=-ol`.
- Makes `CC_D` and `CC_INT` aliases to `CC_`.
- Clears `PCFBASM` to avoid irrelevant PC framebuffer assembler warnings.

Filesystem relevance: Only build-path and shell-command conventions.
