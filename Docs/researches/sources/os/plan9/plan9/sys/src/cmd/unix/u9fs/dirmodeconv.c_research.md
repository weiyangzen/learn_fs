# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/dirmodeconv.c

- Role: Provides a custom `%M` formatter for Plan 9 directory mode bits.
- Key functions: `dirmodeconv` formats `DMDIR`, `DMAPPEND`, `DMEXCL`, and rwx owner/group/other bits into strings like `d-rwxr-xr-x`; `rwx` copies a 3-character permission triplet.
- Integration: Installed by `u9fs.c` with `fmtinstall('M', dirmodeconv)` and used by `fcallconv.c` diagnostics.
- Risks/notes: Uses a static buffer, so it is not thread-safe; this is consistent with the single-threaded u9fs formatter style.
