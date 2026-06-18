# sources/test-tools/ior/src/option.c

Purpose: table-driven command-line and directive parser shared by IOR, mdtest, md-workbench, and backend module options.

Important APIs and functions: `option_parse()` parses `argc/argv` against an `options_all_t` module list. `option_parse_str()` parses a single option token. `option_parse_key_value()` parses legacy `key=value` directives. `option_merge()` concatenates option arrays. `option_print_help()` and `option_print_current()` render help/current values. `string_to_bytes()` parses integer strings with k/m/g/t/p suffixes.

Control flow: `option_parse()` counts required options, iterates argv from index 1, and delegates each token to `option_parse_token()`. The token parser supports `--long`, `--long=value`, short options, compact repeated flags like `-vvv`, and short option values attached to the same token. It searches every registered module and writes directly into the target variable pointer using the option type code.

State and persistence: parser state is local, but parsed values mutate caller-owned variables. String arguments are duplicated with `strdup()` and become caller-owned. Help and error paths print to stdout and exit the process.

Dependencies and integration: exposed by `option.h`; used by parse_options, mdtest, md-workbench, and AIORI module option tables. Depends only on libc and the project option definitions.

Risks: parser mutates argv strings temporarily when handling `=`. `option_parse_key_value()` builds a 1024-byte stack string with `sprintf`. Optional arguments are effectively required once the option is present. Ambiguous module option names can set multiple variables because parsing continues through all modules after a match. Long-option detection relies on string length and `txt[0] == '-'` after stripping the first dash. The code exits on help/errors, which is awkward for library embedding.

Test signals: unit tests should cover suffix parsing, repeated flags, `--name=value`, missing values, hidden strings, module-prefixed long options, required option counting, and duplicate option names across modules.
