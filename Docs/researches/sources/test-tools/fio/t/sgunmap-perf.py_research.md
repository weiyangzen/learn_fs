# sources/test-tools/fio/t/sgunmap-perf.py

Purpose: manual performance comparison tool for fio's `sg` ioengine. It trims a character device with a reference fio build, then compares random read and random write IOPS between candidate and reference builds.

Important APIs and functions: `fulldevice()` runs a full-device trim-like fio job and returns JSON job data. `runtest()` runs one time-based sg workload with configurable rw, queue depth, batch size, block size, and runtime. `runtests()` repeats `runtest()` and returns per-trial total IOPS plus the mean.

Control flow: `main()` parses character device, block device, candidate fio, and reference fio. It trims the character device with the reference build, runs five candidate and five reference random-read trials, then five candidate and five reference random-write trials, printing means and trial lists. The parsed block device argument is present but not used in the executed sequence.

State and persistence: the character device is destructively trimmed and exercised with sg I/O. Results are printed to stdout; no artifacts are written.

Dependencies and integration points: requires Python 2/3 compatibility imports, `six.moves.range`, fio builds that emit JSON, an sg character device, and sufficient permissions. It is not included in the main `run-fio-tests.py` manifest despite a TODO mentioning sgunmap tests.

Risks and test signals: this is performance observation rather than pass/fail validation; it does not exit non-zero for regressions or compare candidate/reference statistically. Risks include destructive device trimming, unused `bdev`, and sensitivity to device state and host load. Signals are printed IOPS means and trial variance.
