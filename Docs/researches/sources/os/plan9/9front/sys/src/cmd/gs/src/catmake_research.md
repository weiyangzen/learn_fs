# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/catmake

This is a short shell script that expands makefile `include` lines.

Key responsibilities:
- Usage: `catmake orig.mak > makefile`.
- Runs an `awk` script over the input file.
- For lines matching `^include `, prints a marker `# INCLUDE OF <file>`, reads the included file, and emits non-comment lines from it.
- For all other lines, prints the original line.

Important behavior:
- Only recognizes include lines beginning exactly with `include `.
- Removes comment lines from included files only, not from the parent file.
- Does not recursively expand include directives inside included content unless they are later encountered in the parent stream.
- Uses shell/awk redirection to read the included path from `$2`.

Notable risks:
- Minimal error handling.
- Include paths are taken directly from makefile text.
- Build helper only; no filesystem implementation logic beyond reading files for makefile flattening.

Research classification: simple Ghostscript makefile preprocessing utility.
