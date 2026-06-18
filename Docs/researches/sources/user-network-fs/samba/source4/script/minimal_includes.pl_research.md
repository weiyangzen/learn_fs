<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/script/minimal_includes.pl -->
# sources/user-network-fs/samba/source4/script/minimal_includes.pl

## Purpose

`minimal_includes.pl` searches C files for top-level `#include` lines that can be removed without changing compiler output, optionally removing them.

## Important APIs, Types, and Functions

Options include `--remove`, `--skip-system`, `--waf`, and `--help`. Important functions are `load_lines()`, `save_lines()`, `test_compile()`, `test_include()`, `process_file()`, and `ShowHelp()`.

## Control Flow

For each input file, the script captures original compile output. It scans top-level include lines outside preprocessor conditionals and not marked `needed`. For each include, it temporarily renames the source to `.misaved`, writes a version without that include, recompiles via `make` or waf, compares output with the original, and either reports or removes the include. Otherwise it restores the original file.

## State and Persistence Behavior

In report mode it should restore files after each test. In `--remove` mode it can persist include removals by deleting the saved original. It creates temporary `.misaved` files during processing and object files during compilation.

## Dependencies and Integration Points

It depends on Perl, local build tooling, `make` or waf, and source files that map predictably to object targets.

## Risks and Edge Cases

The script deliberately edits files during tests, so interruption can leave `.misaved` files or modified sources. Comparing compiler output may miss semantic changes that still compile. Conditional includes are skipped only via simple nesting tracking.

## Test Signals

Tests should run on disposable files with removable and required includes, nested preprocessor blocks, `system/` includes under `--skip-system`, waf mode, and interruption recovery.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/script/minimal_includes.pl -->
