# File Research: sources/os/bsd/freebsd-src/sys/kern/genoffset.sh

## Summary
Shell script that turns `__assym_offset__` symbols from an object file into a generated C include containing lite structure layouts and static offset assertions.

## Main Behavior
The script accepts `[-o outfile] objfile`. It emits include guards, then, when not compiling with `GENOFFSET` and not in an untied KLD module, reads decimal `nm` output for `__assym_offset__` symbols, sorts by structure and offset, and generates `struct <name>_lite` definitions with padding arrays and target fields.

## Validation
For each emitted field it appends `_Static_assert(__builtin_offsetof(struct s_lite, f) == o, ...)`, then undefines the helper macro. This lets generated structure shims validate expected offsets at compile time.

## Inputs and Outputs
Uses `${NM:-nm}` with `${NMFLAGS}` and standard shell tools `grep`, `sed`, and `sort`. With `-o`, output goes to the selected file; otherwise stdout is used.

## Risks
The script depends on exact symbol naming and sort layout after replacing double underscores. A malformed or unexpected symbol name can corrupt generated structure syntax.
