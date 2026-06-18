# File Research: sources/local-fs/xfsprogs/db/attrset.c

Implements expert-mode attribute commands: `attr_list`/`alist`, `attr_get`/`aget`, `attr_set`/`aset`, and `attr_remove`/`aremove`. Commands require the current cursor to be an inode. They support user/root/secure/parent namespaces and `-Z` filesystem-property mode, which validates and translates fs property names through `libfrog/fsproperties.h`.

`attr_set_f` parses create/replace/upsert modes, names from argv or file (`-N`), values from literal strings, generated buffers (`-v`), or files (`-V`), then uses `libxfs_iget`, `libxfs_attr_sethash`, and `libxfs_attr_set`. `attr_remove_f` removes through the same libxfs update path. `attr_get_f` looks up values using a max-length request with libxfs allocating the value buffer. `attr_list_f` allocates an empty transaction, walks attrs with `xattr_walk`, filters namespaces, and optionally fetches/prints values.

Because this code mutates metadata in expert mode, risk centers on direct libxfs operation against the current inode, memory ownership of name/value buffers, and fs-property validation. It refreshes the current inode after set/remove to keep the interactive cursor coherent.
