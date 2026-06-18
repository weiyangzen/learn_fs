
<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/packaging/release.py -->
# Research: sources/sync-backup/rsync/packaging/release.py

## Purpose
`packaging/release.py` is rsync's step-driven maintainer release workflow. Each `--step-N-*` invocation performs one release action, using `../release` for persistent mirrors, scratch data, and a JSON state file shared across steps.

## Important APIs, Types, and Functions
- Constants define `RELEASE_DIR`, `FTP_DIR`, `HTML_DIR`, `WORK_DIR`, `STATE_FILE`, `HTML_SRC`, remote samba paths, and `GEN_FILES`.
- `STEPS`, `STEP_FLAGS`, and `STEP_FUNCS` implement the step registry.
- State helpers: `load_state()`, `save_state()`, `require_samba_host()`, `require_top_of_checkout()`, `replace_or_die()`, `section()`, `confirm()`.
- Step functions: `step_1_fetch()`, `step_2_prepare()`, `step_3_tweak()`, `step_4_build()`, `step_5_commit()`, `step_6_tag()`, `step_7_tarball()`, `step_8_update_ftp()`, `step_9_toplinks()`, `step_10_push_ftp()`, `step_11_push_html()`, and `step_12_push_git()`.
- `rsync_with_confirm()` wraps dry-run-then-confirm for pushes.

## Control Flow
`main()` parses exactly one step flag or `--list`, installs a SIGINT handler, sets `LESS`, and dispatches to the selected function. Step 1 mirrors ftp/html content from a samba host and snapshots `rsync-web`. Step 2 interactively derives release version, previous version, rpm release, protocol-change metadata, source directories, date strings, and writes `release-state.json`. Step 3 edits version, protocol, NEWS, and spec files, runs `year-tweak`, and shows a diff. Step 4 runs source preparation, configure, build, and `make gen`. Steps 5 and 6 commit and sign a tag. Step 7 creates source tarball and diffs using git archive plus generated files. Step 8 refreshes ftp README/NEWS/INSTALL/html, ChangeLog, and signatures. Step 9 updates top-level hard links for final releases. Steps 10 and 11 push ftp/html after dry runs. Step 12 prints git push and announcement instructions.

## State and Persistence
Persistent state lives in `../release/release-state.json`; release artifacts and mirrors live under `../release/rsync-ftp`, `../release/rsync-html`, and `../release/work`. Several steps modify the source checkout (`version.h`, `rsync.h`, `NEWS.md`, specs, generated files), create git commits/tags, write tarballs/diffs/signatures, and update remote samba directories. The script is intentionally manual and interactive at key gates.

## Dependencies and Integration Points
It imports `pkglib` helpers, calls `rsync`, `git`, `tar`, `gzip`, `fakeroot`, `gpg`, `make`, `configure`, `prepare-source`, `md-convert`, `support/git-set-file-times`, and `packaging/year-tweak`. It expects `RSYNC_SAMBA_HOST` to identify a samba.org host. It integrates with release docs (`NEWS.md`), generated manual/html files, rpm spec files, and the `rsync-web/` subtree.

## Risks
This script performs high-impact filesystem, git, signing, and remote sync operations. Risks include stale format regexes for NEWS/spec/version files, accidental operation on the wrong branch or dirty checkout, interactive prompts blocking unattended use, reliance on external host layout and `.filt` filters, shell-command strings with interpolated paths, and partial release state if a step fails midway. `step_5_commit()` commits all tracked changes with `git commit -a`, so unrelated tracked edits in the checkout would be swept into the release commit.

## Test Signals
Use a disposable checkout with fake `../release`, mocked samba host, and fixture `NEWS.md`/spec files to test step 2 state generation and step 3 rewrites. Dry-run tests for steps 7-9 should verify tarball names, diff paths, generated-file inclusion, and hard-link behavior. Manual release rehearsals should confirm gpg, fakeroot, rsync filters, and html/ftp mirror permissions.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/packaging/release.py -->
