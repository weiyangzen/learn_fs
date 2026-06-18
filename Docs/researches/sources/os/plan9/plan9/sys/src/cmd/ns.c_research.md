# File Research: sources/os/plan9/plan9/sys/src/cmd/ns.c

Implements `ns`, a namespace dumper/replayer for a target process. It reads `/proc/<pid>/ns`, parses namespace records, quotes arguments, and prints shell commands that reconstruct the namespace.

By default, mount records whose new side is `/net/.../data` are translated into a more stable network address by reading the corresponding `/net/<net>/<port>/remote`. The `-r` flag disables that translation and preserves raw namespace paths.

The parser accepts several namespace line forms, including `cd`, bind/mount forms with or without flags, and optional specs. It rejects malformed line widths to avoid emitting ambiguous reconstruction commands.

The `quote` helper emits single-quoted strings only when needed for whitespace or shell metacharacters.
