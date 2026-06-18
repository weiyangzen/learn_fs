# File Research: sources/local-fs/ntfs-3g/ntfsprogs/attrdef.h

Small guarded header declaring `extern const unsigned char attrdef_ntfs3x_array[2560];`.

It is consumed by `mkntfs` support code that needs the static NTFS 3.x `$AttrDef` byte image from `attrdef.c`. The only invariant is that the declared size stays synchronized with the array definition and the formatter’s expected `$AttrDef` size.
