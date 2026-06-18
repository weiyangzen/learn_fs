<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/path.py -->
# sources/sync-backup/bup/lib/bup/path.py

## Purpose
This module computes bup runtime paths: executable directory, library/resource directory, default repository, cache locations, and default filesystem index paths.

## Important APIs, Types, And Functions
Public APIs include `exe()`, `exedir()`, `cmddir`, `libdir()`, `resource_path()`, `defaultrepo()`, `xdg_cache()`, `index_cache()`, `FSIndexPaths`, `flat_fsindex()`, and `default_fsindex()`.

## Control Flow
Import-time constants derive from `__file__`: `_libdir`, `_resdir`, `_exedir`, and `_exe`. `defaultrepo()` returns `BUP_DIR` or `~/.bup`. `index_cache(identifier)` prefers an existing XDG cache path, falls back to an existing legacy repo cache, and otherwise returns the XDG target.

## State And Persistence Behavior
The module stores computed path constants and reads environment variables (`BUP_DIR`, `XDG_CACHE_HOME`). It does not create directories itself. `FSIndexPaths` packages the stat, metadata, and hardlink index paths used by index/save flows.

## Dependencies And Integration Points
It is used by `git.auto_midx()` to find the bup executable, by `main.py` to find command executables, by repo selection for default repository paths, and by index/save commands for cache locations.

## Risks And Edge Cases
Path computation assumes the command directory is adjacent to the library as `../cmd`; packaging changes could break this. The file imports `environ` from both `os.environb` and `bup.compat`, relying on the latter final binding. `index_cache()` only checks existence before choosing legacy cache, so migration behavior depends on prior filesystem state.

## Test Signals
Repo/default-path behavior appears in `test/int/test_repo.py`, `test/int/test_git.py`, `test/ext/test-init`, command startup tests, and index tests that use `default_fsindex()`.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/path.py -->
