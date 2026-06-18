# File Research: sources/os/bsd/freebsd-src/sbin/geom/core/geom.h

## Purpose

Defines the ABI contract between the generic `geom` command and GEOM class command libraries.

## Key Definitions

- `G_LIB_VERSION` = 5
- Command flags:
  - `G_FLAG_VERBOSE`
  - `G_FLAG_LOADKLD`
- Option types:
  - bool, string, number, done, multi
- `G_OPT_MAX`
- Sentinel macros:
  - `G_OPT_SENTINEL`
  - `G_NULL_OPTS`
  - `G_CMD_SENTINEL`

## Structures

- `struct g_option`: option character, kernel/request name, default value, and type flags.
- `struct g_command`: command name, flags, optional local handler, option table, and usage string.

## Integration Notes

Class libraries export command tables using these definitions, and `geom.c` consumes them dynamically or statically.
