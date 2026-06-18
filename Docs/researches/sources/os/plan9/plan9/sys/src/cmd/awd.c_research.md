# File Research: sources/os/plan9/plan9/sys/src/cmd/awd.c

Acme window-directory helper.

Key behavior:
- Opens `/dev/acme/ctl`; exits silently if acme is not available.
- Gets current working directory, removes trailing slash.
- Writes acme control commands in single writes using `xfprint()`:
  - `name <cwd>/-<arg-or-rc>`
  - `dumpdir <cwd>`
- `xfprint()` uses `vsmprint` then one `write()` so commands are not split by buffered `fprint`.

Filesystem relevance:
- Direct namespace interaction with `/dev/acme/ctl` and current working directory, but not filesystem implementation code.
