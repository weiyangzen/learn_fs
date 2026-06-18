# File Research: sources/os/plan9/plan9/sys/src/cmd/srvfs.c

Small wrapper that starts `exportfs` and posts the resulting pipe in `/srv`.

Key responsibilities:
- Builds an `exportfs` argv with selected options.
- Creates a pipe to the exportfs child.
- Sends the exported path to the child and expects `OK`.
- Posts the pipe fd to `/srv/name` or an absolute srv path.

Options:
- `-d`, `-R`, `-P patternfile` forwarded to exportfs.
- `-e exportfs`: custom exportfs binary.
- `-p perm`: permission for srv file.

Risks/quirks:
- Fixed `arglist[16]` is enough for current options but not dynamically checked.
- Assumes exportfs handshake returns exactly `OK`.
