<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/workgen_stat.sh -->
# sources/storage-engines/wiredtiger/bench/workgen/runner/workgen_stat.sh

Purpose: shell utility that combines WiredTiger JSON statistics time-series files and Workgen `sample.json` into a sorted output file, optionally opening/running an analyzer.

Important APIs and functions: shell functions `Usage` and `Filter`. `Filter` removes `"version"` fields using `sed`, which helps normalize JSON lines before sorting.

Control flow: parse `-h` home, `-o` output, and `-e` analyzer; verify home directory and `WiredTiger.wt`; choose a temporary output if analyzer is requested without output; run `(cd $wthome; Filter WiredTigerStat.* sample.json) | sort > $outfile`; if analyzer is set, use `open -a` on Darwin or execute analyzer on other systems.

State and persistence: reads stats files from a WT home and writes the combined output file, defaulting to `$wthome/stat_tmp.json` when needed.

Dependencies and integration: POSIX shell, `sed`, `sort`, `uname`, macOS `open` optionally, and analyzer executable. Used after Workgen benchmark runs.

Risks: usage text says at least one of `-t2` or `-o`, but `-t2` is not parsed; likely stale help. Unquoted `$wthome` in `cd $wthome` and `$outfile` redirection can fail for spaces. Glob with no `WiredTigerStat.*` may pass literal depending shell settings.

Test signals: non-empty combined JSON output and analyzer launch/exit status.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/workgen_stat.sh -->
