# sources/sync-backup/rsync/testsuite/append-shortsum_test.py

Purpose: regression for `--append-verify` redo with a negotiated strong checksum shorter than legacy 16-byte sums, specifically forced `xxh64`.

Important APIs/types/functions: JSON `run_rsync('-VV')`, `make_data_file`, `run_rsync('--append-verify', '--checksum-choice=xxh64', '--no-whole-file')`, `assert_same`, and `test_skipped`.

Control flow: skip if `xxh64` is unavailable. Create a 40KB source, write a corrupted 20KB prefix in destination, then run append-verify with xxh64 and no-whole-file. The run must complete and destination must match source.

State and persistence behavior: destination starts as a corrupt prefix so append-verify must append, detect whole-file verification failure, and redo via normal delta/inplace logic.

Dependencies and integration points: checksum negotiation, append redo generator/sender protocol, and xxhash support.

Risks and test signals: pre-fix failure was protocol incompatibility due to overstated `s2length`. The signal is nonzero rsync or mismatched final file.
