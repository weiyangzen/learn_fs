# sources/sync-backup/borg/src/borg/archiver/repo_info_cmd.py

## Purpose

`repo_info_cmd.py` implements `borg repo-info`, displaying repository identity, location, version, encryption/key-storage details, security directory, cache info, or equivalent JSON. The source was read as a complete 75-line file.

## Important APIs, Types, and Functions

`RepoInfoMixIn.do_repo_info()` opens the repository with cache and read compatibility, builds `basic_json_data()` with `security_dir`, formats encryption state from `manifest.key.NAME` and key storage, appends keyfile location when relevant, and prints text or JSON. `build_parser_repo_info()` registers `--json`.

## Control Flow

The command obtains the active key and base info. JSON mode prints the info directly. Text mode builds an `encryption` string distinguishing encrypted, authenticated, and plaintext modes, maps `KeyBlobStorage.KEYFILE`/`REPO` to user-facing storage labels, includes key file location for keyfile storage, formats repository ID/location/version/security directory, appends cache path when present, and prints.

## State and Persistence Behavior

The command is read-only. It may open cache/security metadata for reporting and writes only stdout. No manifest or repository mutation is intended.

## Dependencies and Integration Points

It depends on `basic_json_data()`, `bin_to_hex()`, cache security manager state, repository location/version/id, key storage constants from shared constants, and key methods like `find_key()`. It complements `key_cmds.py` and `repo_create_cmd.py` by reporting the key mode they configure.

## Risks and Edge Cases

Authenticated modes are not encrypted but still have key storage, so text must avoid saying data is encrypted. `KeyBlobStorage` constants are imported through wildcard constants, which hides the dependency. Some info cache objects may not expose `path`; the code checks with `hasattr`. Key classes without storage or `find_key()` need graceful formatting.

## Test Signals

Tests should cover plaintext, encrypted repokey, encrypted keyfile, authenticated key modes, JSON output, cache path presence/absence, security directory inclusion, and keyfile location formatting.
