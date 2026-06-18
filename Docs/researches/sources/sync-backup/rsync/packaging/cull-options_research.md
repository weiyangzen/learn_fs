
<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/packaging/cull-options -->
# Research: sources/sync-backup/rsync/packaging/cull-options

## Purpose
`packaging/cull-options` is a Python generator that scans `../options.c` and emits Perl or Python data tables describing the rsync server options that restricted `rrsync` should recognize. It keeps wrapper option policy synchronized with the options that `server_options()` may send.

## Important APIs, Types, and Functions
- Module dictionaries `short_no_arg`, `short_with_num`, and `long_opts` accumulate option names and argument-checking modes.
- `main()` reads `../options.c`, applies regexes against `argstr[x++]`, `asprintf`, literal `args[ac++]`, `safe_arg()`, and `alt_dest_opt()` patterns, then prints generated code between start/end comments.
- `str_assign()` emits either Python assignment syntax or Perl `our $...` syntax based on command-line mode.
- The CLI is `--python` by default with mutually exclusive `--perl`.

## Control Flow
The script seeds tables with known special options, walks `options.c` line by line, infers short options without args, short options with numeric args, long options with no args, long options with inline args, and long options whose next argv element needs path checking. A one-line `last_long_opt` state tracks whether a preceding literal long option is followed by `safe_arg("", value)`. After scanning it forces `files-from` to mode `3`, prints disabled-option settings, then prints a sorted `long_opts` table.

## State and Persistence
State is in-memory only; output goes to stdout for inclusion in generated `rrsync` code. The script depends on being run from `packaging/` or another directory where `../options.c` is the rsync option source.

## Dependencies and Integration Points
It depends on Python `re` and `argparse`, and on the exact formatting/style of `options.c`. Its output is consumed by `rrsync`, so it indirectly protects restricted rsync deployments from unexpected server-side options.

## Risks
The scanner is regex- and style-dependent. New `server_options()` patterns can be missed if they do not match existing regexes, which can make `rrsync` reject valid options or, more seriously, fail to classify an argument-bearing option for path checking. It also hard-codes extra BackupPC options and special disables, so policy drift needs review when option semantics change.

## Test Signals
Run the script after option changes and diff the generated block in `rrsync`. Add tests that introduce representative `server_options()` additions with no arg, inline arg, split path arg, short numeric arg, and alt-dest return paths. Restricted `rrsync` integration tests should cover subdir path checking for `--files-from`, alt-dest, and backup/temp/partial path arguments.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/packaging/cull-options -->
