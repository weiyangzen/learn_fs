# File Research: sources/local-fs/xfsdump/restore/getopt.h

## Summary
Centralizes the xfsrestore/xfsdump command-line option string and symbolic option-character names so modules that parse their own options use a consistent `getopt(3)` specification.

## Main Contents
- Defines `GETOPT_CMDSTRING` with the complete option set, including option letters that require arguments.
- Maps option characters to descriptive macros such as `GETOPT_WORKSPACE`, `GETOPT_DUMPDEST`, `GETOPT_SUBTREE`, `GETOPT_TOC`, `GETOPT_FORCE`, `GETOPT_FMT2COMPAT`, and `GETOPT_RINGLEN`.
- Documents which subsystem consumes many options, usually `content.c`, `drive.c`, `global.c`, `media.c`, or `getopt.c`.
- Reserves or notes unused letters and platform-specific history.

## Risks
The command string and per-option macros must stay synchronized. A macro added without the matching command-string entry, or vice versa, will make module-local parsing disagree.

This header encodes shared CLI ABI. Scripts and users may depend on these exact option letters and argument requirements.
