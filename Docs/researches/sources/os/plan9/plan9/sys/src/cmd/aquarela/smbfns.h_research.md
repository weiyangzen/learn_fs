# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbfns.h

Function prototype header for Aquarela SMB implementation.

Major contents:
- Endian conversion prototypes.
- SMB command handler declarations.
- Allocation, validation, string conversion, response, tree/service, globals, buffer, client, transaction, trans2, id-map, search, error, time/path/mode, file, log, shared-file, listener, RAP client, directory cache, regexp, open, rune conversion, truncate, remove, and browse prototypes.
- Optional `LEAK` macros for allocator substitution.

Interactions:
- Included through `headers.h` and provides cross-file contracts for the full SMB implementation.

Notable details:
- Declares many functions implemented outside this grouped file set, especially transaction encode/decode, string/time conversion, tree/search, and trans2 handlers.
