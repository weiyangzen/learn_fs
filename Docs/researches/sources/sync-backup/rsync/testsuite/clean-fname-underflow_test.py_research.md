# sources/sync-backup/rsync/testsuite/clean-fname-underflow_test.py

Purpose: regression for `clean_fname()` buffer underflow and mis-collapse when handling `..` in a crafted server-side merge filter name.

Important APIs/types/functions: direct rsync server invocation using the binary from `RSYNC`, `subprocess.run`, `--server --sender -vlr --filter=merge a/../test`, and `test_fail`.

Control flow: create a workdir with `mod`, run rsync in server sender mode with the crafted filter filename, discard output, then require a nonzero non-signal exit.

State and persistence behavior: no successful transfer state is expected. The tested state is parser/path-cleaning rejection without crash.

Dependencies and integration points: rsync internal server mode and filter merge-file path cleaning.

Risks and test signals: exit >=128 means crash; exit 0 means bogus input was accepted or mis-collapsed. Correct behavior is a clean nonzero rejection.
