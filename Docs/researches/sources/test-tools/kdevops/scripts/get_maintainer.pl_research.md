# sources/test-tools/kdevops/scripts/get_maintainer.pl

## Purpose
This Perl script is the Linux `get_maintainer.pl` helper carried into kdevops. It maps a patch or a `-f` file/directory argument to maintainers, reviewers, mailing lists, status, SCM, web, bug, and subsystem information from `MAINTAINERS`, optionally augmented with git or Mercurial history, blame data, `Fixes:` commit signers, keywords, `.mailmap`, and file-local email extraction.

## Important APIs, Types, And Functions
The script is procedural, with global option/state variables set by `Getopt::Long`. The central API is `get_maintainers()`, fed by `@files`, `@fixes`, `@range`, parsed `@typevalue`, and keyword state. `read_all_maintainer_files()` discovers one or more MAINTAINERS files, while `read_maintainer_file()` records raw section lines and converts `F:`/`X:` glob-like patterns to regexes. Matching is handled by `file_match_pattern()`, `find_starting_index()`, `find_ending_index()`, `add_categories()`, `push_email_addresses()`, and role helpers. VCS integration is abstracted through `%VCS_cmds_git` and `%VCS_cmds_hg`, with `vcs_exists()`, `vcs_file_signoffs()`, `vcs_file_blame()`, `vcs_find_signers()`, and `vcs_assign()` doing command dispatch and ranking.

## Control Flow
Startup loads optional `.get_maintainer.conf` and `.get_maintainer.ignore`, parses options, enforces mode constraints, verifies the kernel tree unless `--no-tree`, and reads MAINTAINERS data. Arguments are either treated as files/directories under `-f` or parsed as patches; patch parsing extracts changed filenames, hunk ranges for blame, `Fixes:` hashes, and keyword hits. `get_maintainers()` scans every MAINTAINERS section for matching `F:`, `X:`, and `N:` rules, records exact pattern matches, adds selected categories, scans file-local addresses, adds keyword matches, then optionally adds history/blame/fixes-derived identities. Interactive mode loops over a numbered list and can toggle sources or rerun discovery. Output is role-annotated or plain, multiline or separator-joined.

## State And Persistence
Persistent inputs are `.get_maintainer.conf`, `.get_maintainer.ignore`, `.mailmap`, MAINTAINERS files, and VCS history. Runtime state is global and reset inside `get_maintainers()` before each run. There is no durable output file; results are printed to stdout and warnings to stderr. Self-test mode caches MAINTAINERS line metadata in `@self_test_info` and probes links/SCM endpoints.

## Dependencies And Integration Points
It depends on Perl core modules `Getopt::Long`, `Cwd`, `File::Find`, `File::Spec::Functions`, external `git`, `hg`, and `wget` for optional probes, and the Linux MAINTAINERS schema. It is intended for mail tooling such as `git send-email --cc-cmd`, but `--roles`/`--rolestats` may break consumers expecting bare addresses.

## Risks And Test Signals
VCS commands are built as shell strings with interpolated filenames and commits; quoting depends on upstream assumptions and unusual paths can be risky. Regex-converted MAINTAINERS patterns are powerful but can overmatch or under-match. Network self-tests are slow and flaky. `--git-blame` is explicitly expensive and can surface stale owners. Test signals include `--self-test`, known MAINTAINERS pattern fixtures, mailmap cases, patch parsing with renames/hunks/Fixes, and running with/without git and hg repositories.
