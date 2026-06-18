# sources/test-tools/ltp/testcases/kernel/fs/binfmt_misc/binfmt_misc02.sh

Purpose: LTP test that valid binfmt_misc registrations recognize matching files, do not recognize mismatches, and stop recognizing after disabling the entry.

Important APIs/types/functions: `TST_CNT=6`, `recognised_unrecognised`, `unrecognised`, `verify_binfmt_misc`, `do_test`, `get_binfmt_misc_mntpoint`, `remove_binary_type`, `tst_res`, data files under `$TST_DATAROOT`, shell `eval`, `grep`, `head`, and `cat`.

Control flow: `do_test` registers extension and magic rules with several delimiters. Valid cases run the target data file and require output to contain either extension or magic test text, then write `0` to the binfmt entry and require the same execution to fail or omit that text. Invalid-match cases register rules that should not match the data file and require nonrecognition. Each case removes the binfmt entry after checking.

State/persistence behavior: transiently creates and disables binfmt_misc entries. It writes a `temp` output file in the LTP temporary directory.

Dependencies/integration: sources `binfmt_misc_lib.sh`, needs root, mounted binfmt_misc, installed data files, `cat`, `head`, and LTP harness variables.

Risks/test signals: uses `eval` on file paths, so inputs must remain controlled. Failure signals are explicit TFAIL results for registration, recognition, disable, or mismatch behavior.
