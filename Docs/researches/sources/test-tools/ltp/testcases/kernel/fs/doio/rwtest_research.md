# sources/test-tools/ltp/testcases/kernel/fs/doio/rwtest

Purpose: shell wrapper that connects `iogen` to `doio`, handling option pass-through, generated test-file sizing, optional cleanup, named LTP reporting, and a few legacy scenarios.

Important APIs/types/functions: `usage`, `help`, `killkids`, `cleanup_and_exit`, shell arrays `F[]`, `df`, `dirname`, `${LTPROOT}/testcases/bin/iogen`, `${LTPROOT}/testcases/bin/doio`, and LTP `tst_resm` reporting.

Control flow: parses wrapper flags (`-c`, `-F`, `-S`, `-N`, `-n`) while separating iogen options from doio options, expands percentage file-size specifications using `df`, creates missing directories, and defaults doio flags to `-av`. With `-F` it only prints processed file specs; otherwise it runs `iogen ... files | doio ...`, forces `-k` locking for multi-process I/O, propagates iogen failures via `HUP`, and reports pass/fail from doio's exit status.

State/persistence behavior: can create directories and test files, and with `-c` removes those created by this invocation. Percentage sizing depends on current free space. It also manipulates process groups through traps to stop children on interrupt.

Dependencies/integration: expects LTP shell helpers, `LTPROOT`, installed `iogen` and `doio` binaries, `df`, `expr`, `dirname`, and optionally `mpprun` for MPP scenarios.

Risks/test signals: word-splitting of file names means paths with spaces are unsafe. The integer comparison `[[ $2 > 1 ]]` is shell-specific. Success is `TPASS` and exit 0; any iogen/doio nonzero result emits `TFAIL` and exits nonzero.
