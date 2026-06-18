# sources/sync-backup/borg/src/borg/helpers/fs.py

## Purpose
Collects filesystem, path-safety, Borg directory-location, hard-link, deletion, open/stat, unmount, and temp-file helpers.

## Important APIs, Types, And Functions
Directory helpers include `ensure_dir`, `get_base_dir`, `join_base_dir`, `get_keys_dir`, `get_security_dir`, `get_data_dir`, `get_runtime_dir`, `get_cache_dir`, and `get_config_dir`. Path/tag helpers include `dir_is_cachedir`, `dir_is_tagged`, `make_path_safe`, `slashify`, `map_chars`, `get_strip_prefix`, `remove_dotdot_prefixes`, `assert_sanitized_path`, and `to_sanitized_path`. IO helpers include `scandir_inorder`, `secure_erase`, `safe_unlink`, `dash_open`, `O_`, flag constants, `os_open`, `os_stat`, `umount`, and `mkstemp_mode`. `HardLinkManager` stores typed hard-link identity mappings.

## Control Flow
Borg directory resolution combines environment overrides with legacy and non-legacy XDG/platformdirs behavior, creating directories and cache tags when requested. Path sanitization normalizes separators, handles Windows drive letters/reserved characters, rejects `..`, and normalizes to relative paths. `os_open` supports openat-style parent fd/name, optional `O_NOATIME` fallback, and WSL read-only retry workaround. `safe_unlink` tries unlink, handles ENOSPC by truncating only single-link files, then retries.

## State And Persistence
Most helpers are stateless, but directory helpers create directories and cache tag files. `HardLinkManager` stores an in-memory map. `secure_erase`, `safe_unlink`, `umount`, and `mkstemp_mode` modify filesystem or mount state.

## Dependencies And Integration Points
Integrates with platform flags, constants, `platformdirs`, `SaveFile`, process environment sanitation for unmount subprocesses, archive creation/extraction hard-link handling, pattern/path safety, and tests under `helpers/fs_test.py`.

## Risks And Edge Cases
Environment-derived directory paths must avoid root HOME confusion under mount helpers. `make_path_safe` is security-sensitive for legacy archive reads. Secure erase can damage other links unless `avoid_collateral_damage` is true. Windows behavior differs for directories, drive letters, and reserved chars. `safe_unlink` must not truncate multi-link files.

## Test Signals
Tests should cover env precedence, legacy versus non-legacy dirs, cache tag creation, path sanitization and rejection, Windows mapping via monkeypatch, hard-link manager type assertions, `O_NOATIME` fallback paths, ENOSPC unlink recovery, and temp-file mode creation.
