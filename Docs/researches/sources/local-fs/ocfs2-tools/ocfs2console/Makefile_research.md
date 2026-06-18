# File Research: sources/local-fs/ocfs2-tools/ocfs2console/Makefile

This top-level console makefile descends into `blkid` and `ocfs2interface`, installs/generates `ocfs2console.8`, and marks `ocfs2console` as an extra sbin script/program distributed with its manpage template.

It is a simple dispatcher makefile; actual console functionality lives in subdirectories and external script/interface files.
