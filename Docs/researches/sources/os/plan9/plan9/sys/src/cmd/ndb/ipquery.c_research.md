# File Research: sources/os/plan9/plan9/sys/src/cmd/ndb/ipquery.c

Tiny command-line wrapper around `ndbipinfo()`. It opens an NDB file/root, searches by `attr value`, requests one or more returned attributes, and prints `attr=value` pairs on one line.

It accepts `-f ndb-root`; otherwise it uses default NDB files. It requires at least one search attribute, value, and returned attribute.

Risks are minimal. It does not handle missing result specially beyond printing a blank line and frees the returned tuple list unconditionally.
