<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/build-aux/copyright-year-gen -->
# sources/test-tools/strace/build-aux/copyright-year-gen

Purpose: shell helper that emits the copyright year for generated strace release files.

Important logic: accepts `YEAR_FILE` and optional `DEFAULT_YEAR`. It tries, in order: contents of `YEAR_FILE`, latest Git commit year via `git show -s --format=%cD`, default year, `SOURCE_DATE_EPOCH`, and current UTC year. It validates a non-empty result and prints it without newline.

Control flow: linear fallback chain with usage/error exits.

State and persistence: reads a year file and Git metadata; writes only stdout.

Dependencies and integration: used from `Makefile.am`/configure-generated files to fill copyright year reproducibly.

Risks: relies on GNU `date -d`; portability to non-GNU date is limited. Git command failures are ignored into fallback chain. Test signals: run with `.year`, without `.year` inside Git, and with `SOURCE_DATE_EPOCH` in a non-Git export.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/build-aux/copyright-year-gen -->
