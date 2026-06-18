# File Research: sources/os/bsd/netbsd-src/lib/librumpuser/build-aux/depcomp

Read completely: 791 lines.

## Purpose
Vendored Automake dependency-tracking helper that runs a compiler and produces normalized make dependency files as side effects.

## Main Responsibilities
- Requires `depmode`, `source`, and `object` environment variables.
- Computes default dependency and temporary dependency file paths under `${DEPDIR-.deps}`.
- Supports many compiler dependency modes: `gcc3`, `gcc`, `sgi`, `aix`, `tcc`, `pgcc`, `hp2`, `tru64`, `msvc7`, `dashmstdout`, `makedepend`, `cpp`, `msvisualcpp`, and `none`.
- Converts or post-processes compiler-specific dependency output into makefile fragments keyed by the requested object file.
- Adds dummy dependency targets for headers to avoid make failures after headers are deleted.
- Handles libtool-specific dependency file locations.
- Uses locking for the Portland compiler mode because that compiler writes dependency files based on the source basename.

## Filesystem Relevance
Build-only. It reads/writes dependency files and temporary files but does not implement filesystem behavior.

## Reliability Notes
- This is broad historical portability code with many compiler/platform branches.
- The script defensively creates dummy depfiles if compilers do not produce dependency output.
- Several branches include workarounds for old `sed`, compiler, and platform behavior.

## Dependencies
- POSIX shell, `sed`, `tr`, `sort`, `grep`, `rm`, `mv`, `mkdir`, `rmdir`, `expr`.
- Optional compiler-specific tools such as `makedepend` and `cygpath`.
