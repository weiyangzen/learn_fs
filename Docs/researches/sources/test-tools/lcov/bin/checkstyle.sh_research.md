# sources/test-tools/lcov/bin/checkstyle.sh

Purpose: Bash helper that checks Perl source formatting with `perltidy`, either for the full file or only for style regressions introduced since a git baseline.

Important APIs/types/functions: shell functions `realpath`, `relpath`, `die`, and `report`; environment variables `PERLTIDY`, `PERLTIDYRC`, `GITBASE`, and `MODE`; commands `mktemp`, `trap`, `diff`, `sed`, `grep`, `git show`, and `perltidy`.

Control flow: the script resolves the repository/tool root, validates `MODE` as `diff` or `full`, creates a temporary directory, and iterates over all file arguments. In diff mode it obtains the baseline version from `git show "$GITBASE:$RELFILE"`, tidies both baseline and working copies, and reports only newly introduced offending lines. In full mode it tidies the working file and reports all differences. Clean files have their `.tdy` output removed; files with issues retain `.tdy` for review or Makefile-driven update.

State/persistence behavior: temporary comparison files are removed by the exit trap. Per-file tidy output is written beside the checked file as `FILE.tdy`; it remains on failures and is deleted on success. The script reads git history but does not change git state.

Dependencies/integration: used by the lcov Makefile `checkstyle` target after it discovers Perl scripts and modules. Requires `.perltidyrc` at the tool root, git history for diff mode, and a working `perltidy` binary.

Risks/test signals: the custom `realpath` shadows system `realpath` and assumes paths exist. Diff mode fails for files absent from the baseline, which can make newly added files require full-mode handling. The report algorithm is line-diff based, so complex rewrites can produce noisy findings. Signals are exit status, printed offending line groups, and presence or absence of `.tdy` files.
