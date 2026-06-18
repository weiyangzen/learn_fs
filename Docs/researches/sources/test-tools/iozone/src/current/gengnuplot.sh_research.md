# sources/test-tools/iozone/src/current/gengnuplot.sh

## Purpose

`gengnuplot.sh` is a small helper that converts `iozone -a` tabular output into a three-column data file suitable for gnuplot. It copies the supplied iozone output into a fixed working file named `iozone_gen_out`, selects one benchmark column based on the requested test name, and writes `record_size file_size selected_metric` rows into a per-test directory.

The script expects exactly two arguments:

- `$1`: an iozone auto-mode output file.
- `$2`: a test selector such as `write`, `rewrite`, `read`, `reread`, `randread`, `randwrite`, `bkwdread`, `recrewrite`, `strideread`, `fwrite`, `frewrite`, `fread`, or `freread`.

## Important APIs and Functions

The only defined function is `write_gnuplot_file()`. It echoes a comment identifying the selected test, then uses a `case` statement over global variable `query`.

Each supported case runs `awk '$1 ~ /^[0-9]+/ { print $1 " " $2 " " $N }' < $file_name`, where `$N` maps to the iozone result column:

- `write` -> column 3.
- `rewrite` -> column 4.
- `read` -> column 5.
- `reread` -> column 6.
- `randread` -> column 7.
- `randwrite` -> column 8.
- `bkwdread` -> column 9.
- `recrewrite` -> column 10.
- `strideread` -> column 11.
- `fwrite` -> column 12.
- `frewrite` -> column 13.
- `fread` -> column 14.
- `freread` -> column 15.

The numeric-row filter skips headers and comments by requiring the first field to begin with a digit.

## Control Flow

At startup, the script runs `cp $1 iozone_gen_out`, sets `file_name=iozone_gen_out`, sets `filename=iozone_gen_out` even though `filename` is not subsequently used, and assigns `query=$2`.

It then runs `if (! [ -e $query ] ) ; then mkdir $query; fi`, creating a directory named after the requested test when no filesystem entry of that name exists. If exactly two arguments are present, it redirects `write_gnuplot_file` output to `$query/$(basename $file_name.gnuplot)`, which resolves to `$query/iozone_gen_out.gnuplot`. Otherwise it prints usage text.

Unsupported test names are handled inside `write_gnuplot_file()` by writing usage text to stderr, but the outer control flow still creates the output directory and output file for the unsupported name.

## State and Persistence Behavior

The script always overwrites or creates `iozone_gen_out` in the current working directory before validating the argument count. It also creates a directory whose name is exactly `$2`, and it writes or truncates `$2/iozone_gen_out.gnuplot` when two arguments are present. Output names are fixed, so repeated runs overwrite the previous copied input and gnuplot data for the same test.

There is no cleanup of the copied `iozone_gen_out` file. The generated files are relative to the caller's current directory, not relative to the source file or input file.

## Dependencies and Integration Points

The script depends on `/bin/sh`, `cp`, `mkdir`, `basename`, and `awk`. It is coupled to the classic iozone `-a` report column order and to gnuplot-style three-column data files. It does not invoke gnuplot itself; it only prepares data files for later plotting.

Its integration point is manual or scripted post-processing after an iozone benchmark run. A caller would run one invocation per desired metric and then point gnuplot at the resulting `iozone_gen_out.gnuplot` files.

## Risks and Edge Cases

- Arguments are unquoted throughout. Input paths, test names, glob characters, whitespace, and leading dashes can break commands or change behavior.
- `cp $1 iozone_gen_out` executes before checking `$#`, so missing arguments produce a `cp` error before the usage text.
- The directory creation test checks `-e $query`; if a non-directory file already exists with the test name, redirection to `$query/iozone_gen_out.gnuplot` fails.
- The script accepts arbitrary `$2` values as path names. A selector like `../out` writes outside the current directory; shell metacharacters can also be dangerous because the value is unquoted.
- The `if (! [ -e $query ] )` syntax is non-idiomatic and may not be portable to all `/bin/sh` implementations even though it works in common shells.
- Unsupported test names still create an output file containing only the `#test` line plus stderr usage output elsewhere, which can look like a successful data generation to weak callers.
- Fixed temporary/output file names make concurrent runs in the same directory race with each other.

## Test Signals

Smoke tests should create a tiny representative iozone table with one numeric row and invoke the script for each supported selector, then assert that the third output column matches the expected input column. Usage behavior should be checked for zero, one, and three arguments.

Edge tests should cover input paths with spaces, unsupported selectors, preexisting non-directory selector names, selector names containing slashes, and concurrent invocations in the same working directory. Since the output file is deterministic (`<selector>/iozone_gen_out.gnuplot`), tests can assert exact output content for known input.
