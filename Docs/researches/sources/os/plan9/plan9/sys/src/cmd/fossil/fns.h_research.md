# File Research: sources/os/plan9/plan9/sys/src/cmd/fossil/fns.h

Private prototype header for the fossil storage implementation.

It declares Source, cache, block, disk, packing, formatting, filesystem, file, archiver, block-watch, walker, snapshot, and checker functions. It also registers the custom `%L` formatter for labels.

This header ties together the lower-level storage modules under `dat.h`.
