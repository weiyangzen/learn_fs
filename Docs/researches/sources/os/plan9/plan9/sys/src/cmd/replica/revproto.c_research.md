# File Research: sources/os/plan9/plan9/sys/src/cmd/replica/revproto.c

Read status: complete, 512 lines.

`revproto.c` implements reverse proto-file enumeration. It parses proto syntax, walks the source tree under `root`, maps paths to an external/rooted destination under `xroot`, applies uid/gid/mode overrides, and calls a callback for every enumerated file.

`revrdproto` sets up parser state and invokes `domkfs`. `getfile`, `getname`, `getmode`, and `getpath` parse indented proto entries. `mktree` expands `+` and `*` recursive/nonrecursive directory wildcards. `copyfile` stats files, adjusts default ownership and permissions, handles explicit proto metadata, and calls the supplied enumerator.

The parser uses indentation depth to model hierarchy and `skipdir` to skip nested proto regions when a directory cannot be read or statted.

Filesystem relevance: high. It is the proto traversal adapter that feeds replica scans and reverse mappings.
