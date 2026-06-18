# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/dvx-tail.mak

Purpose: Shared DesqView/X makefile tail, included after device and feature makefiles.

Key targets:
- Defines `dvx_.dev` from platform objects `gp_getnv`, `gp_dvx`, `gp_unifs`, `gp_dosfs`, `gp_stdin`, and `nosync.dev`.
- Builds `gp_dvx.o` with `-D__DVX__`.
- Provides DesqView/X auxiliary program build rules for `echogs`, `genarch`, `genconf`, `gendev`, `genht`, and `geninit`, using `strip`, `coff2exe`, and `del`.
- Generates `gconfig_.h` with `HAVE_SYS_TIME_H` and `HAVE_DIRENT_H`.
- Links the main Ghostscript executable by copying `ld.tr`, appending extra/standard libs, invoking `gcc`, stripping, converting COFF to `.exe`, and deleting the intermediate.

Notable behavior:
- Uses `.NOEXPORT` to prevent huge environment propagation into command lines.
- Hardcodes `INCLUDE=/djgpp/include` for config generation.

Filesystem relevance: Build artifact creation and generated config only.
