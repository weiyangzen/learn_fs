# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/fmtindex.c

Implements `fmtindex`, which writes or extends the textual index configuration replicated across index sections.

It reads the Venti config, counts all arenas from configured arena partitions, and either creates a fresh `Index` with `newindex()` or loads an existing one with `-a`. It builds a new arena address map starting at `IndexBase`, preserving existing arena map entries when extending and appending new arenas after the prior stop address.

The command reports arena count, index bucket count, and storage bytes, then writes index config and section headers through `wbindex()`. It validates index name legality and existing arena ordering when appending.
