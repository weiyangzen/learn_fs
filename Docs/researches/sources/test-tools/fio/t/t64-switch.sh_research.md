# sources/test-tools/fio/t/t64-switch.sh

Purpose: shell regression test proving fio automatically switches to `tausworthe64` when the file-size/block-size space exceeds the default 32-bit random generator. It compares duplicate offset counts between forced 32-bit and automatic generator selection.

Important operations: it accepts optional fio path and IO count, runs two null-engine random-read fio commands over a 1T file with 1-byte blocks and `--norandommap`, parses `--debug=io` completion offsets with `grep`, `cut`, `sort`, `uniq -D`, and `wc -l`, then computes a duplicate-count ratio.

Control flow: `t32` is measured with `--random_generator=tausworthe`; `t64` is measured without forcing the generator. If `t64` is non-zero the ratio is `t32/t64`, otherwise it is `t32`. The script prints both counts and passes if the ratio is at least 10.

State and persistence: uses the null ioengine and writes no persistent files. It can be CPU-heavy because the default count is one million IOs and debug output is piped through sorting.

Dependencies and integration points: requires bash, fio, and common Unix text tools. It is invoked by `run-fio-tests.py` as executable test 1020 on non-Windows systems.

Risks and test signals: debug-output format changes can break parsing. The output label says `tausworthe62`, a typo for 64. Statistical duplicate ratios may vary with count, but the threshold is intentionally coarse. Success signal is `result: pass` and exit 0; otherwise it prints `result: fail` and exits 1.
