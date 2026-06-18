# File Research: sources/os/plan9/9front/sys/src/cmd/ip/torrent.c

This is a compact BitTorrent client and torrent-file generator.

Key behavior:
- Implements bencode parsing, dictionary lookup, torrent metadata loading, infohash generation, piece map tracking, and SHA1 piece verification.
- Supports single-file and multi-file torrents, path sanitization that replaces spaces with non-breaking spaces, and on-demand directory creation.
- Implements BitTorrent peer handshake and messages: bitfield, have, interested, choke/unchoke, request, piece, cancel, and port.
- Runs incoming peer server, outgoing peer workers, HTTP trackers, UDP trackers, and webseed fetchers.
- `-c` creates a torrent for a file with trackers/webseeds.
- Tracks upload/download/left counters and can print progress.

Research notes:
- Uses `/mnt/web` for HTTP tracker and webseed fetches.
- Peer scheduling picks randomly among missing pieces advertised by a peer.
- The piece message truncation path has suspicious code: `if(o+n > pieces[x].len) n = o - pieces[x].len;`, which can make `n` negative.
