# File Research: sources/os/bsd/netbsd-src/lib/checkver

Shell script that checks whether installed or set-list library versions are newer than a source `shlib_version`. It accepts one source of installed library names: `-d` directory scan, `-s` distribution set lists, or `-f` explicit file.

It derives the library name from an argument, from `LIB=` in the local `Makefile`, or from the current directory basename, then compares matching `lib*.so.*` entries against sourced `major`, `minor`, and optional `teeny`.

The `fixone` helper is intended to parse installed version fields with AWK and report newer installed versions. As written, the AWK code calls `split(LIB, VER, ".")` but prints `V[...]`, which is a source-level issue to note rather than normalize away.
