# File Research: sources/local-fs/ocfs2-tools/o2cb_ctl/Makefile

Build recipe for the legacy `o2cb_ctl` and newer command-style `o2cb` utilities.

It shares config parser/model sources across both tools, links `o2cb_ctl` with `libo2cb`, GLib, libocfs2, com_err, and AIO, and links `o2cb` additionally with `libo2dlm` and `libtools-internal`. It defaults to static linking unless `OCFS2_DYNAMIC_CTL` is set, defines `VERSION`, applies GLib flags per object, and installs man pages for `o2cb`, `o2cb_ctl`, and `ocfs2.cluster.conf`.
