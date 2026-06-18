# File Research: sources/os/plan9/plan9/sys/src/cmd/rio/dat.h

Read status: complete, 342 lines.

This is `rio`’s central data header. It defines synthetic 9P qid identifiers, window control message constants, channel message structs, mouse state queues, the `Window`, `Fid`, `Xfid`, `Filsys`, and `Timer` structs, and the major global variables.

`Window` embeds `Ref`, `QLock`, and `Frame`, and owns images, mouse/keyboard/control channels, text buffers, selection state, raw input buffers, geometry, process identity, cursor state, label, and working directory.

`Filsys` tracks pipe fds, user name, xfid allocator channel, and fid hash buckets. `Xfid` wraps an in-flight 9P request and flush synchronization state.

Filesystem relevance: foundational for `rio`’s synthetic `/dev` filesystem and window-as-file model.
