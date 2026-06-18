# File Research: sources/os/bsd/freebsd-src/sbin/ddb/ddb_script.c

## Purpose
Lists, sets, and removes DDB scripts from userland.

## Main Elements
- Sysctl names for setting one script, listing scripts, and removing a script.
- `ddb_list_scripts()`: obtains full script list, prints all or finds a named script by parsing `name=value` lines.
- `ddb_script()`: sets a script when the argument contains `=`, otherwise prints a named script.
- `ddb_scripts()`: prints all scripts.
- `ddb_unscript()`: removes a named script and maps kernel `EINVAL` to user-facing `ENOENT`.

## Dependencies And Integration
Uses `debug.ddb.scripting.*` sysctls. Called from `ddb.c` dispatcher.

## Risk Notes
Script strings are passed directly to kernel DDB scripting sysctls. Listing parses kernel output format line by line.
