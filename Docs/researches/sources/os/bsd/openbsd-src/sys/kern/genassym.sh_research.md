# File Research: sources/os/bsd/openbsd-src/sys/kern/genassym.sh

Generates assembly-visible constants from a compact input language.

Key behavior:
- Optional `-c` mode generates C, compiles, and executes it to print constants.
- Default mode emits inline assembly markers, compiles to assembly, and extracts `#define` lines from `XYZZY` markers.
- Supports directives: `config`, `include`, preprocessor conditionals, `struct`, `union`, `member`, `export`, `define`, and `quote`.
- Automatically emits `_KERNEL` and a local `offsetof` macro.
- Uses a temporary directory under `/tmp` and cleans it via trap.

Filesystem/OS relevance:
- Kernel build utility for keeping assembly offsets synchronized with C structs.
