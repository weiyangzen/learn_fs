# File Research: sources/os/plan9/plan9/sys/src/cmd/srvold9p/srvold9p.c

Bridge from modern 9P2000 clients to old 9P1 servers.

Key responsibilities:
- Connects to an old 9P service by command, network, file, or stdio.
- Exposes a modern 9P endpoint, optionally posted in `/srv` and mounted.
- Converts 9P2000 requests into 9P1 calls and converts responses back.
- Tracks fids, old/new directory offsets, and outstanding tags for flush handling.

Important architecture:
- `serve`: reads modern 9P requests, dispatches via `fcalls`, and writes modern responses.
- `demux`: reads old 9P1 responses and rendezvous-delivers them by tag.
- `transact9p1`: send old request and wait for matching old response.
- `Tag` list tracks `flushed`, `received`, and refs.
- `Fid` list tracks busy/allocated state and directory offset translation.

Request handlers:
- `rversion`: local version negotiation.
- `rattach`, `rwalk`, `ropen`, `rcreate`, `rread`, `rwrite`, `rclunk`, `rremove`, `rstat`, `rwstat`.
- `dirrread`: converts fixed 9P1 directory records into variable 9P2000 stats.
- `rflush`: forwards flush and wakes blocked rendezvous if needed.

Risks/quirks:
- Authentication is explicitly unsupported in active path.
- Comment notes `demux` assumes one read per message unless paired with `fcall`.
- Directory seeks are disallowed because old/new directory record sizes differ.
