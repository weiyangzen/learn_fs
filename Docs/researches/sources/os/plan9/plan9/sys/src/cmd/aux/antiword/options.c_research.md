# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/options.c

## Summary
`options.c` owns Antiword runtime options. In the Plan 9/non-RISC OS path it parses command-line options, chooses output mode, validates paper sizes, opens character mapping files, and derives defaults from environment state.

## Main Responsibilities
- Stores current options in `tOptionsCurr` with platform-specific defaults.
- Supports text, formatted text, PostScript, PDF, and XML-related command-line switches.
- Handles paper-size names for PS/PDF and computes paragraph width from page dimensions and margins.
- Searches mapping files in `ANTIWORDHOME`, user home Antiword directory, then global Antiword directory.
- Maps selected mapping-file names to internal encoding classes.
- Rejects unsupported output/encoding combinations such as PDF UTF-8, PDF Cyrillic, and PostScript UTF-8.
- Contains RISC OS choices-window UI handlers behind `__riscos`.

## Key Dependencies
Uses `getopt`, environment variables, `szGetDefaultMappingFile()`, `szGetHomeDirectory()`, `bReadCharacterMappingTable()`, and conversion geometry helpers.

## Filesystem Relevance
Important for config-file lookup and mapping-file opening. Plan 9 inherits the non-RISC OS path and Antiword directory constants from `antiword.h`.

## Notes
The mapping-file search logic is path-length guarded and emits warnings rather than silently truncating.
