# File Research: sources/os/bsd/freebsd-src/sbin/ldconfig/ldconfig.c

## Purpose
Provides the main command-line interface for `ldconfig`.

## Main Responsibilities
- Parses compatibility mode prefixes such as `-elf`, `-aout`, and `-32`.
- Chooses the appropriate hints file path.
- Dispatches to list or update ELF hints functions.
- Handles merge, rescan, insecure, big-endian, and custom hints file flags.

## Key Implementation Details
- `-aout` is explicitly unsupported.
- `-elf` is accepted and skipped for compatibility.
- `-32` selects the 32-bit ELF hints path.
- `-B` forces big-endian hints output/validation.
- `-R` requests rescan behavior.
- `-f` overrides hints file.
- `-i` sets global `insecure`.
- `-m` merges with current hints.
- `-r` lists current hints.
- `-s` and `-v` are accepted compatibility no-ops.

## Integration Points
Calls:
- `list_elf_hints()`
- `update_elf_hints()`

## Notable Edge Cases
- With no path arguments and not just reading, it enables rescan.
- Merge is forced when rescanning so existing hints are read before writing.
