# File Research: sources/os/bsd/freebsd-src/sbin/fsck/fsck.c

Implements the generic `fsck` front-end, selecting filesystems and invoking filesystem-specific checker binaries.

Key responsibilities:
- Parses global fsck options, type filters, per-type options, and alternate fstab path.
- If no operands are supplied, checks fstab entries through `checkfstab()`.
- If operands are supplied, resolves devices/mountpoints/fstab entries and runs appropriate `fsck_<type>`.
- Supports preen/clean modes, always-yes/no propagation, force, verbose, debug, and background-check modes.
- Guesses filesystem type from GEOM partition attribute `PART::type` if no fstab/type information is available.

Important functions:
- `isok()` decides whether an fstab entry should be checked now.
- `checkfs()` normalizes filesystem type, builds `fsck_<type>` argv, forks with `vfork()`, and runs `execvP()` in `_PATH_SYSPATH`.
- `selected()` checks `-t` type inclusion/exclusion list.
- `addoption()` stores `-T fstype:options` per-type options.
- `maketypelist()` parses `-t` and `no...` exclusion mode.
- `catopt()` appends comma-separated option strings.
- `mangle()` converts comma-separated options into argv entries, handling dash options and `-o` options.
- `getfstype()` maps partition type hints such as `ufs`, `ffs`, `fat`, and `efi`.

Background check behavior:
- `-B` performs needed background checks.
- `-F` asks filesystem checkers whether checks can be deferred.
- `-B` and `-F` are mutually exclusive.
- Read-only and `noauto` filesystems are excluded from background deferral paths.

Risks and constraints:
- Dispatch model depends on external helper binaries in `_PATH_SYSPATH`.
- Uses `vfork()`, so parent variables are treated carefully.
- Type mapping is intentionally small and heuristic.
- `fsck` itself does not repair filesystems; it orchestrates specific checkers.
