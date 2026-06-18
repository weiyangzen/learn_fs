# sources/sync-backup/bup/lib/bup/config.py

## Purpose
`config.py` provides configuration-related errors and remote option URL parsing for bup's repository abstractions.

## APIs and Control Flow
`ConfigError` is a marker exception used by configuration readers. `url_for_remote_opt(remote)` parses `--remote`-style bytes. It first attempts `parse_bytes_path_url(remote, require_auth=True)` and, if that returns an error/none, falls back to legacy `user@host:path` parsing. It supports ssh, bup, and bup-rev schemes with scheme-specific validation; `host == b'-'` creates an ssh URL without host for subprocess testing.

## State, Dependencies, Integration, Risks, Tests
The module is pure. Dependencies are `URL`, `parse_bytes_path_url`, and `path_msg` for diagnostics. It integrates with repo location helpers used by init/save/split/restore/get and remote client setup. Risks include subtle legacy parsing (`rpartition('@')`, first colon in hostpath), bup URL user/path restrictions, and returning either `URL` or diagnostic string. Test signals include legacy user containing `@`, missing colon/host, ssh test subprocess remote, bup/bup-rev validation, unexpected scheme errors, and bytes diagnostic formatting.
