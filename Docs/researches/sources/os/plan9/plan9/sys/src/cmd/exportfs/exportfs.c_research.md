# File Research: sources/os/plan9/plan9/sys/src/cmd/exportfs/exportfs.c

Main process and shared infrastructure for Plan 9 `exportfs`.

Key behavior:
- Parses options for authentication, debugging, encryption/filtering, message size, namespace file, root service path, readonly mode, posted service fd, exclusion patterns, announce string, and back-calling import address.
- Optionally authenticates with p9any, changes user namespace, disallows `none`, and supports SSL negotiation for new import protocol.
- Establishes service root from `-s`/`-r`, posted service fd, back-call import, or path read from the network connection.
- Initializes root `File` records and qid uniquification tables.
- Reads 9P messages with `localread9pmsg()`, decodes to `Fcall`, and dispatches through `fcalls`.
- `reply()` serializes `Fcall` replies to the network fd.
- Manages fid hash table allocation/freeing, including unmounting per-fid mount points.
- Maintains `File` tree cache with refcounts, parent/child lists, path construction, exclusion checks, and fresh `dirstat()` data.
- Maps real `Dir` qids to unique exported qids, resolving qid collisions by using high path bits.
- `filter()` negotiates an auxiliary listener and execs an external filter such as `aan`.
- `fatal()` kills slave worker processes before exiting.

Filesystem relevance:
- Core export server setup, connection negotiation, fid/cache management, and qid mapping for exporting a Plan 9 namespace over 9P.
