# File Research: sources/os/plan9/9front/sys/src/cmd/auth/lib/log.c

Auth database success/failure logging helper.

Key responsibilities:
- Writes `bad` or `good` messages to `<db>/<user>/log`.
- Applies bad/good records to both Plan 9 key DB and network key DB.
- `fail(user)` logs failure and exits with `failure`.

Dependencies:
- Uses `KEYDB`, `NETKEYDB`, and keyfs `log` file semantics.
