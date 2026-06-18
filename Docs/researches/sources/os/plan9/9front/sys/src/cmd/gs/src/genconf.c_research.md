# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/genconf.c

Build-time `.dev` configuration merger. It reads Ghostscript module definition files and emits configuration headers and object/library transfer files.

Key behavior:
- Parses `.dev` token streams with categories such as `-dev`, `-dev2`, `-comp`, `-font`, `-functiontype`, `-halftone`, `-imageclass`, `-imagetype`, `-include`, `-init`, `-iodev`, `-lib`, `-libpath`, `-link`, `-obj`, `-oper`, `-plugin`, `-ps`, and `-replace`.
- Recursively reads included `.dev` files, caching file contents and avoiding duplicate work when possible.
- Tracks each resource with its source-file index so `-replace` can remove all entries contributed by a replaced module.
- Maintains resource lists with uniqueness policies: first occurrence, last occurrence, or all occurrences.
- Emits `gconfig.h` style macro calls, `gconfigf.h` font entries, and object/library/linker lists depending on command-line output switches.
- Supports formatting patterns for object/library outputs, with uppercase and extension-dropping options.

Notable dependencies:
- Standard C file/string allocation APIs only; this is a standalone build utility.
- Output macro names must match consumers documented in `gsconfig.c` and the Ghostscript make rules.

Research notes:
- `mrealloc` intentionally allocates/copies instead of using `realloc` for portability across older systems.
- Pattern substitution uses `%s` internally and repeats the item up to three times for patterns needing multiple substitutions.
- This is build configuration infrastructure, not runtime filesystem code.
