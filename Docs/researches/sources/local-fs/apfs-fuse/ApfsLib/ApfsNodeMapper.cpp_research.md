# File Research: sources/local-fs/apfs-fuse/ApfsLib/ApfsNodeMapper.cpp

This file contains only the trivial constructor and virtual destructor definitions for the abstract `ApfsNodeMapper` base class.

There is no mapping behavior here. Implementations are supplied by `CheckPointMap` and `ApfsNodeMapperBTree`.

Its purpose is ABI/linkage support for the polymorphic mapper interface used by `BTree` and container/volume object-map resolution.
