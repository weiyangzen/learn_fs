# File Research: sources/os/plan9/9front/sys/src/cmd/git/query.c

Reference/query command. It resolves expressions via `resolverefs` and prints hashes, optionally as full `git/fs` object paths with `-p`, in reverse with `-r`, or as changed paths with `-c`.

Change mode compares the tree of the first resolved commit against each later commit. `difftrees` recursively walks sorted tree entries and emits status prefixes for removed (`-`), added (`+`), mode-changed (`!`), and content-changed (`@`) paths. Directory changes recurse to file-level entries.
