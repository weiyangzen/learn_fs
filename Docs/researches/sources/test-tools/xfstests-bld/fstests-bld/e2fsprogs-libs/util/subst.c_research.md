# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/util/subst.c

Purpose: `subst.c` is a small build-time template substitution program used to expand `@NAME@` and `${NAME}`-style placeholders into configured values.

Important APIs, types, and functions: `struct subst_entry` stores linked-list substitutions. `add_subst()`, `fetch_subst_entry()`, `get_subst_symbol()`, `replace_string()`, `substitute_line()`, `parse_config_file()`, `compare_file()`, and `main()` implement the tool. CLI options are `-f config-file`, `-t` to adjust timestamp on unchanged output, and `-v` for verbose logging.

Control flow: config files are parsed into a linked list of name/value substitutions, ignoring comments, blank lines, and future-extension lines beginning with `@`. Input is read from a file or stdin. Each line first expands `@FOO@`, handling `@@` as a literal `@`, then expands `${FOO}` by looking up a key with `$` prefix. Output goes to stdout or to `outfn.new`. When writing a named output, it compares the new file with the existing file; unchanged output keeps the old file and optionally updates mtime, changed output renames `.new` into place. The final output file is chmodded read-only for user/group/other write bits.

State and persistence: maintains an in-memory substitution table for the process. It writes generated files, may update timestamps, removes temporary `.new` files on unchanged output, and changes output file mode to read-only.

Dependencies and integration points: used by e2fsprogs build templates such as manpages, headers, pkg-config files, and generated scripts. It consumes `subst.conf.in` after configuration and uses standard C/POSIX file APIs.

Risks: fixed 2048-byte line buffers can truncate long lines. `replace_string()` can grow a line in-place without knowing the full allocated capacity, so large replacement values can overflow the stack buffer. The substitution table never frees entries, acceptable for short build-tool process lifetime. `parse_config_file()` comment stripping treats `#` anywhere as comment, so values cannot contain literal `#`. Missing `@FOO@` emits an error but does not fail the process.

Test signals: unit-style runs for `@NAME@`, `@@`, `${prefix}` with `$`-prefixed config keys, unchanged output preservation, timestamp update mode, missing substitutions, long replacements, and generated file permissions.
