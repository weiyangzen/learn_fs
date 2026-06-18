# sources/user-network-fs/samba/source3/winbindd/idmap_hash/mapfile.c

## Purpose
This file implements simple bidirectional lookup against the optional `idmap_hash:name_map` text file used by the hash NSS-info backend. The file format is line-oriented `key=value`, with whitespace trimming around each side.

## Important APIs, Types, And Functions
The public functions are `mapfile_lookup_key`, which searches by value and returns the matching key, and `mapfile_lookup_value`, which searches by key and returns the matching value. Helpers include `mapfile_open`, `mapfile_read_line`, and `mapfile_close`. The module uses a static `FILE *lw_map_file`.

## Control Flow
Each lookup opens or rewinds the configured file, loops through parsed lines with `mapfile_read_line`, compares using `strequal`, talloc-duplicates the result into the caller context, then closes the file. `mapfile_read_line` strips newline and carriage returns, splits at the first `=`, copies both halves into `fstring` buffers, and trims spaces.

## State And Persistence
The persistent source is the external map file named by `lp_parm_const_string(-1, "idmap_hash", "name_map", NULL)`. The static file handle is opened per lookup and closed before return. There is no cache, locking, reload notification, or validation beyond line parsing.

## Dependencies And Integration
The code depends on Samba configuration access, fstring/string wrappers, talloc, and the hash NSS-info hooks in `idmap_hash.c`. It is used for alias normalization rather than core SID/ID hashing.

## Risks And Test Signals
Malformed lines stop that line but the loop continues only if the next read succeeds; very long lines are truncated to 1023 bytes. There is a concrete defect in `mapfile_lookup_value`: after `*value = talloc_strdup(...)`, it checks `if (!*key)` even though `key` is the input key string, not the output pointer; as written this is either a compile failure or an incorrect allocation check depending on compiler context. Tests should cover missing config, missing file, empty file, whitespace trimming, duplicate keys/values, long lines, malformed lines, and allocation-failure paths.
