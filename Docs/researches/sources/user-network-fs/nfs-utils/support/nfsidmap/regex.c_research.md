# sources/user-network-fs/nfs-utils/support/nfsidmap/regex.c

Purpose: `regex.c` implements a configurable regex-based idmap plugin that extracts local account/group names from remote NFSv4 names and formats local names back into remote names.

Important APIs and control flow: `regex_init` reads `Regex/User-Regex`, `Group-Regex`, prefix/suffix options, optional `Group-Name-Prefix`, and optional prefix-exclusion regex. `regex_getpwnam` and `regex_getgrnam` run `regexec`, use the first captured submatch as the local name, optionally remove group prefixes, then call `getpwnam_r`/`getgrnam_r`. ID/name callbacks wrap those helpers, `write_name` composes reverse mappings, and principal callbacks accept `krb5` or `spkm3`.

State, dependencies, and integration: Compiled regexes and string pointers are global plugin state sourced from libnfsidmap configuration. It depends on POSIX regex, NSS, and shared buffer-size helpers.

Risks and test signals: `regex_init` returns success even after missing or failed regex compilation in the error path, which can leave uninitialized regex state. Reverse formatting uses repeated `strcat`, and input names are not escaped because regexes intentionally control parsing. Tests should cover missing config, bad regexes, capture selection, prefix exclusion, reverse output length, and group-list overflow.
