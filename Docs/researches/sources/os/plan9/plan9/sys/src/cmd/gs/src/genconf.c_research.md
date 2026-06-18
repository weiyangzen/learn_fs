# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/genconf.c

Read status: complete.

Purpose: build-time generator that reads Ghostscript `.dev` module description files and emits merged configuration outputs such as `gconfig.h`, `gconfigf.h`, object lists, library lists, and linker switch lists.

Input model:
- `.dev` files contain switches like `-dev`, `-dev2`, `-include`, `-init`, `-oper`, `-ps`, `-font`, `-lib`, `-obj`, `-replace`, and other resource categories.
- `-include` recursively reads another `.dev` file, adding `.dev` if no suffix is present.
- `-replace` removes resources associated with a replaced module.

Main data structures:
- `string_item_t` records a string, source file index, and insertion index.
- `string_list_t` stores resource lists with uniqueness modes: keep all, keep first, or keep last.
- `string_pattern_t` controls output pattern formatting, uppercase conversion, and extension dropping.
- `config_t` owns all accumulated file names, file contents, replacement declarations, resource lists, and output patterns.

Main logic:
- `main` initializes lists, parses command-line switches, reads `.dev` files, and writes requested outputs.
- `read_file` loads each `.dev` file into memory and caches contents by file name.
- `read_dev` tokenizes a `.dev` file and calls `add_entry` for each resource.
- `add_entry` maps categories to generated macros such as `device_(...)`, `init_(...)`, `oper_(...)`, `psfile_(...)`, `function_type_(...)`, and `image_type_(...)`.
- `process_replaces` removes all resource entries originating from files named by `-replace`.
- `sort_uniq` sorts by string, removes duplicates according to uniqueness policy, and optionally restores insertion order.
- `write_list_pattern` expands formatted output and wraps macro-like resources in matching `#ifdef` / `#endif` guards.

Filesystem/storage relevance:
- Reads build-description files and writes generated build/config files.
- Implements build dependency flattening and resource list generation rather than runtime filesystem code.

Notable behavior and risks:
- Uses fixed-size buffers such as `MAX_STR` and unchecked `strcpy`/`strcat` in several places, relying on historical build inputs.
- `mrealloc` allocates/copies but does not free the old allocation, acceptable only because this is a short-lived generator.
- Tokenization is whitespace-based and does not implement quoting.
