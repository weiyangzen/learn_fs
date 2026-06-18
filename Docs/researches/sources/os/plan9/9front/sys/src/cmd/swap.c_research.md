# File Research: sources/os/plan9/9front/sys/src/cmd/swap.c

`swap.c` configures a file as Plan 9 swap backing.

Behavior:
- Usage: `swap file`.
- If the argument is a directory, creates a temporary file named from `$sysname` or `swap` under that directory with `mktemp`.
- If the argument is an existing non-directory, opens it read/write.
- If needed, creates the swap file with `ORDWR|ORCLOSE`, mode `0600`, and marks it `DMTMP|0600`.
- Resolves the path with `fd2path`, stores it in environment variable `swap`, prints it, then writes the file descriptor number to `/dev/swap`.

Integration:
- `/dev/swap` accepts an fd number for the kernel/device swap setup.
- `ORCLOSE` and `DMTMP` make directory-created swap files temporary.

Risks:
- Uses `mktemp`-style name generation, consistent with Plan 9 but traditionally race-prone in other environments.
- Only accepts one argument and exits fatally on most failures.
