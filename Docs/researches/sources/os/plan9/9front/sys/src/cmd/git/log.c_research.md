# File Research: sources/os/plan9/9front/sys/src/cmd/git/log.c

Implements `git/log`. It resolves either an expression with `-e` or a starting commit with `-c`/default `HEAD`, walks commits by commit time using `Objq`, and prints either full logs or short one-line logs with `-s`. `-n` limits emitted messages.

Path filtering is handled by a trie-like `Pfilt`. Each commit's tree is compared against each parent tree only along requested path components, so a commit is shown only when relevant paths changed. Root commits compare against an empty tree. Full output includes hash, author, optional committer, local formatted date, and indented message body.
