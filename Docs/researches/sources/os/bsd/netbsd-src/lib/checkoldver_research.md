# File Research: sources/os/bsd/netbsd-src/lib/checkoldver

Shell script that scans installed library directories and prints older shared-library filenames that can be removed. Its intended use is piping output to `xargs rm -f`.

It iterates `lib*.so`, compares versioned siblings with major/minor/tiny components, and prints obsolete paths using the current directory. The comparison logic tracks the highest version seen per library basename.

Notable implementation detail: one tiny-version comparison branch references `$5` even though parsed version fields are assigned to `$1`, `$2`, and `$3`; the report should preserve that as source behavior.
