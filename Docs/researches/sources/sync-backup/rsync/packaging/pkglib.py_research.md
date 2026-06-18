
<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/packaging/pkglib.py -->
# Research: sources/sync-backup/rsync/packaging/pkglib.py

## Purpose
`packaging/pkglib.py` is a shared Python helper library for rsync packaging and release scripts. It wraps subprocess execution, git state checks, generated-file discovery, and version/protocol parsing from rsync source files.

## Important APIs, Types, and Functions
- `warn()` and `die()` are stderr/error-exit helpers.
- `_tweak_opts()` centralizes subprocess defaults: `shell=True` for string commands, UTF-8 encoding unless `raw=True`, capture modes, and discard modes.
- `cmd_run()`, `cmd_chk()`, `cmd_txt()`, `cmd_txt_chk()`, and `cmd_pipe()` provide common subprocess patterns.
- `check_git_status()` and `check_git_state()` validate branch/cleanliness, with optional extra checkout handling.
- `latest_git_hash()` and `get_patch_branches()` inspect git history/branch naming.
- `get_gen_files()` reads `GENFILES` from `auto-build-save/<branch>/Makefile`.
- `get_rsync_version()`, `get_NEWS_version_info()`, and `get_protocol_versions()` parse `version.h`, `NEWS.md`, and `rsync.h`.

## Control Flow
Most helpers are leaf routines. Subprocess wrappers call `_tweak_opts()` then `subprocess.run()` or `Popen()`. Git checks run command-line git, parse status text, and may prompt before proceeding if branch expectations differ. Version helpers open source files and regex-match defines or NEWS table rows, exiting via `die()` if required signals are absent.

## State and Persistence
The only module-level state is `default_encoding`. `set_default_encoding()` attempts to change it, but because it does not declare `global default_encoding`, it currently creates a local variable and does not update module state. Other functions are stateless except for subprocess side effects and user prompts.

## Dependencies and Integration Points
The library is imported by `packaging/release.py` and likely other packaging scripts. It assumes an rsync source checkout with git available and specific source-file formats. `get_gen_files()` integrates with `prep-auto-dir`'s branch-specific `auto-build-save` layout.

## Risks
The subprocess wrapper defaults string commands to shell execution, so callers must not pass unsanitized input as a string. Git status parsing is text-format dependent. Interactive prompts in `check_git_state()` can block automation. `set_default_encoding()` is a likely bug if callers expect it to disable or change encoding globally. `get_gen_files()` assumes a generated Makefile exists in the auto-build directory.

## Test Signals
Unit tests can monkeypatch subprocess calls to verify capture/discard/raw options, branch parsing, and error propagation. Fixture tests should cover `version.h`, `rsync.h`, `NEWS.md`, and Makefile `GENFILES` parsing. A regression test should assert `set_default_encoding(None)` changes later subprocess behavior if that function is intended to work.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/packaging/pkglib.py -->
