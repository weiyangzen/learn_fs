# File Research: sources/local-fs/ocfs2-tools/ocfs2cdsl/Makefile

This makefile builds `ocfs2cdsl` as a root sbin program from `ocfs2cdsl.c`. It uses `libocfs2`, `libo2dlm`, `libo2cb`/optional dlm_lt, GLib flags/libs, and `com_err`.

It defines `VERSION` and `G_DISABLE_DEPRECATED`, installs/generates `ocfs2cdsl.8`, and includes distribution rules. The resulting tool is GLib-heavy despite linking mostly through common build variables.
