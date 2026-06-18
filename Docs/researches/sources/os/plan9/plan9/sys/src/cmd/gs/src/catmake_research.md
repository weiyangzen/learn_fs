# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/catmake

This is a small shell/awk helper that expands simple makefile `include` directives.

Behavior:
- Usage: `catmake orig.mak > makefile`.
- For lines matching `^include `, prints a marker `# INCLUDE OF <file>`.
- Reads the included file named by the second field.
- Emits included lines except those beginning with `#`.
- Emits all non-include lines unchanged.

Limitations:
- Handles only simple `include <file>` syntax.
- Does not recursively expand nested includes unless they appear in the included content and are reprocessed by awk input flow, which this script does not explicitly arrange.
- Does not preserve comments from included files.

Filesystem relevance is build-time file reading only.
