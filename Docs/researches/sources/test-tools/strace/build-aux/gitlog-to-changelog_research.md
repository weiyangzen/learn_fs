<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/build-aux/gitlog-to-changelog -->
# sources/test-tools/strace/build-aux/gitlog-to-changelog

Purpose: GNU-derived Perl script that converts Git log output into traditional ChangeLog format.

Important APIs/functions: shell prologue re-execs Perl. Options include `--amend`, `--append-dot`, `--no-cluster`, `--srcdir`, `--since`, `--until`, `--ignore-matching`, `--ignore-line`, `--format`, `--strip-tab`, and `--strip-cherry-pick`. Helper functions include `usage`, `shell_quote`, `quoted_cmd`, `parse_amend_file`, and `git_dir_option`.

Control flow: parses options, builds `git log --log-size --pretty=format:%H:%ct  %an  <%ae>...`, reads exact byte-sized entries, optionally applies Safe-compartment amendments, strips metadata lines, handles co-authors/tiny-change markers, clusters adjacent entries by date/author, and prints ChangeLog paragraphs.

State and persistence: reads Git history and optional amend files; writes ChangeLog text to stdout. It tracks previous author/date/coauthor state for clustering.

Dependencies and integration: used by `Makefile.am` maintainer target for generated `ChangeLog`.

Risks: amend files execute restricted Perl substitutions but still add complexity. Log parsing assumes Git output format invariants. Timezone/localtime affects formatted dates. Test signals: run with `--since`, compare generated ChangeLog stability, and validate unused amend entries fail.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/build-aux/gitlog-to-changelog -->
