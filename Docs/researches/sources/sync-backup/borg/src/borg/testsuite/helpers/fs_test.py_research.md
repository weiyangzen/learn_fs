# sources/sync-backup/borg/src/borg/testsuite/helpers/fs_test.py

Purpose: tests filesystem helper path resolution, safe deletion, path sanitization, cache/tag detection, dash stdio handling, and Windows character mapping.

Important APIs and control flow: environment tests cover `get_base_dir`, `get_config_dir`, `get_cache_dir`, `get_keys_dir`, `get_security_dir`, and `get_runtime_dir` across Windows, Darwin, and other POSIX branches, including `BORG_*` overrides and XDG variables. `dash_open` maps `-` to stdio streams. Hardlink-skipped tests ensure `safe_unlink` does not destroy a hardlinked victim and still preserves it on simulated `ENOSPC`. Path tests exercise `remove_dotdot_prefixes`, `make_path_safe`, rejected dot-dot paths, and Windows drive-letter normalization. `test_dir_is_tagged` creates real directories with valid/invalid `CACHEDIR.TAG` and custom tag files, then tests both path and directory-fd lookup modes. `test_map_chars` verifies Windows private-use substitutions for reserved filename characters.

State and persistence: writes temporary directories, files, hardlinks, tag files, and environment variables. Directory tag detection reads both path-based and fd-relative state.

Dependencies and integration points: depends on `helpers.fs`, Borg cache-tag constants, platform flags, and testsuite helpers for hardlink support and rejected dot-dot paths. These helpers are used by repository/key/cache path discovery and archive extraction safety.

Risks: platform-specific defaults are branchy and can be fragile under MSYS/Cygwin, Haiku, CI runtime-dir layouts, or unusual HOME/USER settings. Path safety must reject traversal without over-normalizing legitimate names.

Test signals: exact path outputs under controlled env vars, hardlink victim preservation, expected `ValueError`, tag lists for every directory case, and Windows character mapping.
