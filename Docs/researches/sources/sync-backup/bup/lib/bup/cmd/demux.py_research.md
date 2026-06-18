# sources/sync-backup/bup/lib/bup/cmd/demux.py

## Purpose
`demux.py` is an internal stream demultiplexer used by remote execution, especially `bup on`, to recover a child command's stdout/stderr framing from a multiplexed channel.

## APIs and Control Flow
`main(argv)` rejects all positional arguments, flushes local stdout/stderr, wraps stdout with `byte_stream`, then opens a `DemuxConn` on stdin's file descriptor and `/dev/null` as the outgoing control sink. It reads lines from `DemuxConn.readline` until EOF and writes them to stdout.

## State, Dependencies, Integration, Risks, Tests
It depends on `bup.helpers.DemuxConn`, `byte_stream`, and option parsing. It persists no state; its only observable behavior is stream forwarding. It is tightly coupled to `cmd/mux.py` and `cmd/on.py` framing conventions. Risks are protocol drift, binary data assumptions around `readline`, and unexpected arguments from callers. Test signals include rejection of arguments, exact forwarding of muxed stdout, stderr flush behavior, and clean flush on exceptions/EOF.
