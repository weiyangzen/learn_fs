# File Research: sources/os/plan9/plan9/sys/src/cmd/pcc.c

Implements `pcc`, a Plan 9 APE C compiler driver. It chooses architecture-specific compiler/linker tools from `$objtype`, runs `cpp`, pipes to the selected C compiler, and optionally links with APE libraries.

The architecture table maps Plan 9 objtypes to compiler, linker, object suffix, and output name. Source `.c` inputs become architecture-suffixed objects; matching object/archive files are passed to the linker; wrong-architecture objects are ignored with a warning.

Flags are split between preprocessor, compiler, linker, and driver behavior. `-E` and `-P` stop after preprocessing; `-c` stops after compilation; `-o` selects output; `-l` maps to architecture APE libraries; `-v` prints commands.

`dopipe` forks compiler and preprocessor around a pipe and waits for both. The linker appends `/arch/lib/ape/libap.a` and removes the temporary single object after successful link unless it is an archive.
