# File Research: sources/local-fs/squashfs-tools/squashfs-tools/pseudo.h

Defines pseudo file type flags and predicates: process-backed, data-backed, and other pseudo entries. Declares metadata structs for pseudo stat data, shared pseudo data files, data extents, pseudo devices, tree entries, pseudo directories, and pseudo xattr lists.

Exports parser/tree APIs including definition reading, default pseudo directory parsing, pseudo file parsing, subtree lookup/iteration, dynamic command execution, global tree access, trace dump, path element parsing, and tree search.

This header is shared by pseudo parsing, xattr pseudo additions, and reader logic.
