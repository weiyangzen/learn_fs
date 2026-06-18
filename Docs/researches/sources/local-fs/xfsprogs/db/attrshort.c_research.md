# File Research: sources/local-fs/xfsprogs/db/attrshort.c

Defines field layouts for inode-local shortform attributes. It exposes the shortform header (`totsize`, `count`) and variable-length entry list. Each entry includes name/value lengths, flags, decoded namespace bits (`root`, `secure`, `parent`), name bytes, parent-pointer value decoding, and ordinary value bytes.

Dynamic callbacks compute entry sizes, list offsets, name/value counts, and suppress ordinary values when the entry is a parent-pointer attr. `attrshort_size` walks all entries from the header to compute the total shortform byte span. This is parser/printing metadata only, relying on libxfs shortform entry traversal helpers and on byte-aligned structures.
