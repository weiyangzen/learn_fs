# sources/test-tools/iozone/src/current/report.pl

Purpose: older Perl report generator for iozone output. It extracts benchmark rows, creates gnuplot scripts for 3D and 2D graphs per metric, and runs gnuplot to produce PNG files in a `report_*` directory.

Important APIs/types/functions: script-level variables `@Reports`, `%columns`, `$outdir`, `@datafiles`, and per-column gnuplot filehandles drive behavior. `%columns` maps throughput metrics to iozone output columns 3 through 15; unlike `iozone_visualizer.pl`, it omits axis columns from the map.

Control flow: reject no reports, option-looking names, or paths containing `/`; derive and recreate the output directory; for each report, write `<basename>.dat` and `2d-<basename>.dat` from numeric rows with at least eight fields; put rows in the 2D file when record length is `16384` or equals file size; for every metric, write `$column.do` and `2d-$column.do`, run both through gnuplot in the output directory, and print `(ok)` or `(failed)`.

State/persistence behavior: destructively removes a same-named `report_*` output directory and persists `.dat`, `2d-*.dat`, `.do`, and PNG files. It does not write HTML and does not mutate the input reports.

Dependencies/integration: depends on core Perl, shell `rm -rf`, and gnuplot. It expects iozone text output in the historical numeric table format and is effectively superseded by the stricter `iozone_visualizer.pl`.

Risks/test signals: no `use strict`/warnings, two-argument `open`, shell interpolation, and permissive row width (`>= 8`) make it less robust than the newer visualizer. It also uses hash iteration order for graph generation. Test with a known report should produce all metric PNGs and correctly filtered 2D data.
