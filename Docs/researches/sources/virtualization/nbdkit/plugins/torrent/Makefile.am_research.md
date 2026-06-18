# File Research: sources/virtualization/nbdkit/plugins/torrent/Makefile.am

Builds the BitTorrent-backed plugin when both C++ and libtorrent support are available.

Key behavior:
- Distributes `nbdkit-torrent-plugin.pod`.
- Guards build with `HAVE_CXX` and `HAVE_TORRENT`.
- Builds `nbdkit-torrent-plugin.la` from `torrent.cpp` and the public plugin header.
- Adds common include paths and local include path.
- Uses pthread and libtorrent compiler/linker flags.
- Links nbdkit common utils, pthreads, libtorrent, and Windows import library support.
- Adds plugin linker script when enabled.
- Generates `nbdkit-torrent-plugin.1` when POD support is available, inserting magic-parameter docs.

Dependencies:
- C++ compiler.
- libtorrent/rasterbar.
- pthreads.
- nbdkit common utils.
