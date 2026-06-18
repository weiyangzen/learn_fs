# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/macos-mcp.mak

## Purpose
Makefile that generates a Metrowerks CodeWarrior XML project from a Darwin/Mac OS X host for building Ghostscript targeting classic Mac OS/Carbon.

## Main Structure
- Defines Ghostscript source/generated/object directories and includes `version.mak`.
- Sets classic Mac runtime paths, feature selection, bundled third-party library settings, compiler/linker stubs, device lists, and build feature modules.
- Includes the normal Ghostscript make fragments with `CC=echo` so dependency/link traces can be generated rather than compiled.
- Adds Mac device/platform module rules and auxiliary generator builds with real `cc`.
- Generates `ghostscript.mcp.xml` by copying `macsystypes.h` to generated `sys/types.h`, invoking `macgenmcpxml.sh` over `ldt.tr`, and copying generated config source files.

## Important Build Products
- `macos.dev`: Mac display/device module.
- `macos_.dev`: platform module containing Mac file/IO/stdin/glue objects plus `gp_getnv`, `gp_nsync`, `gdevemap`, and `gsdll`.
- `macpoll.dev`: polling feature for interpreter builds.
- `ghostscript.mcp.xml`: CodeWarrior import project.

## Integration Notes
- Includes `gs.mak`, `lib.mak`, `int.mak`, fonts, JPEG, zlib, libpng, jbig2, Jasper, icclib, devices, contrib, and Unix end fragments.
- The default `GS_XE` target depends on link trace generation and XML generation rather than producing a normal Unix executable.

## Risks and Edge Cases
- `CC=echo` means normal compile commands are intentionally not real; auxiliary tools use `CCAUX=cc`.
- Assumes `/Developer/Tools/SetFile` exists.
- IJS is commented out as not ported to Mac OS Classic.
- Full device list is large and may produce project/library filename issues when combined with `macgenmcpxml.sh` limitations.
