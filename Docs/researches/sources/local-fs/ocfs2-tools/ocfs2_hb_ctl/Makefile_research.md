# File Research: sources/local-fs/ocfs2-tools/ocfs2_hb_ctl/Makefile

This makefile builds `ocfs2_hb_ctl` as a root sbin program. It links against `libocfs2`, `libo2dlm`, `libo2cb`, `com_err`, AIO, and optional fsdlm/cmap stack libraries. Unless `OCFS2_DYNAMIC_CTL` is set, it adds static linking.

It installs/generates `ocfs2_hb_ctl.8` and distributes the single C source plus manpage template. The build defines `VERSION`.
