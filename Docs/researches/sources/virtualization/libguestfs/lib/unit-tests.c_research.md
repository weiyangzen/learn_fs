# File Research: sources/virtualization/libguestfs/lib/unit-tests.c

Internal unit tests for small libguestfs utility functions.

Important behavior:
- Tests string split, concat, join, GUID validation, drive name/index conversion, umask retrieval, command helper basics, qemu parameter escaping, timeval difference, regex match helpers, stringsbuf behavior, and string validation macros.
- Creates libguestfs handles but does not launch appliances.
- `test_command` covers argv-style and shell-style command helper use with touch/rm.
- `test_valid` mirrors validation macros from drive parsing for formats, disk labels, and hostnames.
- Uses `assert` throughout and exits success if all tests pass.

Filesystem relevance:
- Protects utility functions that underpin drive naming, parsing, validation, temporary command execution, and launch diagnostics.
