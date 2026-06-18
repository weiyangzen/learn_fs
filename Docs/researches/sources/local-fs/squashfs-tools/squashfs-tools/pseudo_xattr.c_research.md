# File Research: sources/local-fs/squashfs-tools/squashfs-tools/pseudo_xattr.c

Adds pseudo xattr definitions into the same pseudo tree used for pseudo files. `read_pseudo_xattr()` delegates parsing to `xattr_parse()`.

`add_pseudo_xattr_definition()` special-cases root `/`, either appending to an existing root pseudo or wrapping the current tree under a new root node. Non-root paths recurse through components using `get_element()` and `pseudo_search()` from `pseudo.c`.

Each target accumulates a `pseudo_xattr` list with count and linked `xattr_add` entries.
