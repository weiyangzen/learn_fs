# sources/test-tools/fio/tools/plot/samples/Makefile

Purpose: sample driver Makefile demonstrating how to unpack archived fio logs and run the plot tooling for IOPS and bandwidth examples.

Important targets: `all` depends on cleanup, extraction, `io`, and `bandwidth`. `m2sw1-128k-sdb-randwrite-para.results_bw.log` extracts `fio-logs.tar.gz`. `setup` symlinks plot scripts/templates from the parent directory. `io` and `bandwidth` call `./fio2gnuplot.py` with read-parallel IOPS or bandwidth glob patterns and `-g` rendering. `clean` removes generated PNGs, temp scripts, symlinks, math files, extracted log directories, and logs.

Control flow/state: Make target dependencies ensure scripts are symlinked before plot commands. The target writes only generated/symlinked sample artifacts in the sample directory.

Dependencies/integration: assumes `fio-logs.tar.gz`, parent `*py` and `*gpm` files, and a `fio2gnuplot.py` executable name even though this source tree also has `fio2gnuplot` without a `.py` suffix.

Risks/test signals: likely bit-rots if script names change, and cleanup is broad (`*log`, `*py`, `*gpm`). A smoke test would run `make -n` and, with sample archive present, ensure both graph paths produce outputs without deleting source files outside the sample directory.
