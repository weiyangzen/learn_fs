# File Research: sources/os/plan9/9front/sys/src/cmd/ns.c

Prints a shell-reconstructable view of a process namespace.

Key elements:
- Usage: `ns [-r] [pid]`.
- Reads `/proc/<pid>/ns`, tokenizes each namespace operation, and prints it with quoting.
- Supports `cd` lines and mount/bind-like records with 3, 4, or 5 fields.
- `xlatemnt` rewrites mounts of `/net/<proto>/<conn>/data` into `proto!remote` form unless `-r` is set.
- `quote` single-quotes strings containing shell-sensitive characters.

Notable behavior:
- Defaults to current process when no pid is supplied.
- Uses `-r` for raw namespace paths without network translation.

Risks and quirks:
- Fixed buffers and maximum 5 tokens match expected `/proc/ns` format.
- Quoting uses rotating static buffers.
