# File Research: sources/os/linux/linux/fs/ocfs2/mmap.h

`mmap.h` declares `ocfs2_mmap_prepare(struct vm_area_desc *desc)`.

This is the small interface used by OCFS2 file mmap setup to install clustered VM fault/page_mkwrite operations.
