# sources/object-store/minio-mc/cmd/config-fix.go

## Purpose

`config-fix.go` performs targeted repairs for historically broken mc config files before normal migration runs. These fixes handle malformed v3 host JSON, bad v6 glob host entries, v6 hosts missing schemes, and duplicate Windows config locations.

## Important APIs, Control Flow, And State

`fixConfig` orchestrates `fixConfigLocation`, `fixConfigV3`, `fixConfigV6`, and `fixConfigV6ForHosts`. `ConfigAnyVersion` loads only the config version. `fixConfigV3` detects version `3`, loads a `brokenConfigV3`, rewrites hosts through proper `hostConfigV3` JSON tags, drops unused ACL/access fields, and saves only when mutation is detected. `fixConfigV6` rewrites known glob-style host keys to concrete S3/GCS/local defaults and fatals on unsupported glob patterns. `fixConfigV6ForHosts` adds `https://` to known host keys that lack schemes. `fixConfigLocation` handles Windows `.exe` config directory duplication by renaming legacy/current directories depending on invocation path.

## State, Dependencies, Integration, Risks, And Tests

This file mutates `config.json` and config directories via quick config load/save, `os.Stat`, `os.Rename`, and `os.RemoveAll`. It integrates with startup config repair before migration. Risks are fatal exits on load/save issues, key collisions when rewriting hosts, dropping malformed entries not matching known patterns, and Windows rename failure requiring manual intervention. Test coverage is not in this subset; validation likely relies on config migration/fix integration tests elsewhere.
