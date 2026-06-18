# sources/test-tools/iozone/src/current/iozone_visualizer.pl

Purpose: modernized Perl visualizer for one or more iozone text reports. It extracts numeric 15-column benchmark rows, writes normalized 3D and filtered 2D `.dat` files, generates gnuplot scripts for every throughput metric, invokes gnuplot, and writes an `index.html` page linking all generated PNG graphs.

Important APIs/types/functions: uses `Getopt::Long` for `--3d`, `--2d`, and `--nooffset`, `Readonly` for constants, `List::MoreUtils::any` for validation, `Carp`/`English` for errors, and Perl filehandles for report/data/html/script output. The metric map `%columns` indexes iozone columns `KB`, `reclen`, `write`, `rewrite`, `read`, `reread`, `randread`, `randwrite`, `bkwdread`, `recrewrite`, `strideread`, `fwrite`, `frewrite`, `fread`, and `freread`.

Control flow: parse options and default graph sizes; reject missing arguments, option-looking report names, or report paths containing `/`; derive an output directory named `report_<report basenames>`; remove any existing directory with `rm -rf`; create per-report `.dat` and `2d-.dat` files; skip nonnumeric lines and rows that do not have exactly 15 fields; insert blank separators when the file-size column changes; write 2D rows only when record length is `16384` or equals file size; build an HTML menu and graph sections; for each non-axis metric, write 3D and 2D gnuplot scripts, run `gnuplot`, and report per-graph success.

State/persistence behavior: destructive output state is the generated `report_*` directory. It persists `.dat`, `2d-*.dat`, `*.do`, graph PNGs, and `index.html`; it does not mutate source reports. Existing output directory contents are unconditionally deleted before regeneration.

Dependencies/integration: depends on non-core Perl modules `Readonly` and `List::MoreUtils`, local shell `rm`, and `gnuplot` with PNG terminal support. It integrates with iozone `-a` style output where the benchmark table has 15 numeric columns.

Risks/test signals: report filenames are interpolated into shell commands and gnuplot script strings, so the current-directory restriction reduces but does not eliminate quoting risks. `system "rm -rf $outdir"` is destructive if name construction is ever widened. Hash iteration order makes graph order nondeterministic. A practical test is running against a small captured iozone report and checking non-empty `.dat`, `index.html`, `.do`, and PNG outputs plus stderr `(ok)` messages.
