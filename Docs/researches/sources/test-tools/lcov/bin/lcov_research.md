# sources/test-tools/lcov/bin/lcov

## Purpose

`lcov` is the main LCOV command-line wrapper. It provides a single interface for resetting counters, capturing userspace or kernel coverage, packaging raw coverage files, combining tracefiles, extracting/removing files by pattern, listing trace contents, summarizing tracefiles, and computing trace intersections or differences. It delegates raw userspace capture to `geninfo` and delegates trace parsing/aggregation/filtering to `lcovutil`.

## Important APIs, types, and functions

- `%lcov_options` defines the command surface: `--directory`, `--capture`, `--zerocounters`, `--add-tracefile`, `--extract`, `--remove`, `--list`, `--summary`, `--intersect`, `--subtract`, `--to-package`, `--from-package`, kernel directory options, and pass-through geninfo options.
- `check_options()` enforces that exactly one primary action is selected.
- `userspace_reset()` deletes `.da` and `.gcda` files under selected directories using `find`.
- `userspace_capture()` either calls `lcov_geninfo()` or creates a raw coverage package.
- `lcov_geninfo()` constructs a `geninfo` command line and passes through output, test name, base/source directories, checksum, filters, coverage modes, demangling, resolve/version/context scripts, parallel/memory/profile settings, and error-handling options.
- Kernel helpers include `setup_gkv()`, `setup_gkv_sys()`, `setup_gkv_proc()`, `kernel_reset()`, `kernel_capture_initial()`, `kernel_capture()`, `copy_gcov_dir()`, `adjust_kernel_dir()`, and `kernel_capture_from_dir()`.
- Package helpers `create_package()`, `get_package()`, `count_package_data()`, `link_data()`, and related callbacks create or consume tarballs of raw coverage data plus metadata files `.gcov_kernel_version` and `.build_directory`.
- Trace operations use `AggregateTraces`, `TraceFile`, and `TraceInfo`: `add_traces()`, `merge_traces()`, `remove_file_patterns()`, `summary()`, and `emit()`.
- `list()` prints a table of per-file and total line/function/branch/MC/DC rates, using `get_prefix()`, `shorten_filename()`, `shorten_number()`, and `shorten_rate()` for formatting.

## Control flow

Startup installs LCOV signal/error handlers, records the command line, parses rc and command-line options, normalizes compatibility/list/external options, validates mode combinations, auto-detects kernel gcov support when needed, and dispatches to exactly one action.

Dispatch behavior is action-specific:

1. `--zerocounters` resets userspace files if `--directory` is present, otherwise writes to the kernel gcov reset node.
2. `--capture` captures from a package, userspace directory, or kernel gcov tree. Userspace capture normally executes `geninfo`; package/kernel capture may copy/link raw files first.
3. `--add-tracefile` merges tracefiles, optionally emitting function mappings or pruned testcase lists.
4. `--remove` and `--extract` load one tracefile, rely on `lcovutil` pattern state to filter it, and emit the result.
5. `--list` loads one tracefile and prints a formatted coverage table.
6. `--summary` merges tracefiles and prints summary data.
7. `--intersect` and `--subtract` merge base tracefiles from positional arguments with RHS glob patterns and apply a `TraceInfo` merge operation.

After dispatch, it cleans temporary directories, restores the original working directory, prints summaries or "Done", checks coverage criteria, emits warnings/profile data, and exits non-zero on errors or failed criteria.

## State and persistence behavior

Persistent effects depend on mode. Reset mode deletes `.da`/`.gcda` files or writes kernel reset controls. Capture and trace-transform modes write LCOV `.info` output or stdout. Package mode creates `.tar.gz` archives and temporarily writes `.build_directory` and `.gcov_kernel_version` into the package root before removing them. Kernel/package capture copies raw gcov trees into temporary directories and can create symlinks from package data into build directories.

In-memory state is primarily global option variables, `$output_filename`, `$data_stdout`, `$gcov_dir`, `$gcov_gkv`, and arrays of trace patterns. Temporary directory lifecycle is managed by `lcovutil::create_temp_dir()` and `temp_cleanup()`.

## Dependencies and integration points

The script uses Perl modules `File::Find`, `File::Path`, `File::Spec`, `Cwd`, `POSIX`, `Storable`, `Time::HiRes`, `FindBin`, and `lcovutil`. External commands include `geninfo`, `find`, `tar`, `mount`, `modprobe`, and filesystem access to `/sys/kernel/debug/gcov` or `/proc/gcov` for kernel capture. It integrates with LCOV tracefiles, raw GCC coverage data, kernel gcov debugfs/procfs layouts, and release/package workflows.

## Risks and edge cases

- Many file operations shell out with interpolated paths (`find`, `tar`, `mount`, `modprobe`), so unusual filenames or untrusted package names can be risky.
- `--to-package` and `--from-package` depend on tar behavior and temporarily mutate the source/package directory with metadata marker files.
- Kernel capture requires privileges and kernel gcov support; auto-detection may mount debugfs or load modules.
- Symlink management in package capture can fail or leave links if interrupted.
- `lcov_geninfo()` mirrors many options manually. New geninfo options must be added here or `lcov --capture` behavior will diverge from direct `geninfo`.
- `--diff` is still parsed but deliberately errors as deprecated/removed.
- Listing output is width-sensitive and can truncate rates/counts to `#` when values do not fit.
- `remove_file_patterns()` relies on global extract/remove option state in `lcovutil`, so behavior is not obvious from its local argument alone.

## Test signals

Tests should cover invalid combinations, `--capture` pass-through to `geninfo`, userspace reset, package create/read, merge/add, extract/remove, list formatting, summary, intersect/subtract, stdout output, coverage criteria failures, and ignored-error behavior. Kernel paths need privileged or mocked tests for `/sys/kernel/debug/gcov`, `/proc/gcov`, reset files, and module/debugfs setup. Regression tests should compare direct `geninfo` output with `lcov --capture` output for the same fixture.
