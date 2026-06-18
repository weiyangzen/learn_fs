# sources/user-network-fs/nfs-ganesha/src/cmake/githead_from_path.sh

Purpose: Extracts a git head/hash-like token from a path-like input.

Important APIs/types/functions: Splits `$1` on underscores and hyphens, filters tokens containing `git`, strips the literal `git`, and prints `NOT-GIT` if no token remains.

Control flow: Single shell pipeline using `sed`, `grep`, and `sed`; emits one or more matching stripped tokens depending on input.

State and persistence behavior: Stateless utility; no persistence.

Dependencies and integration points: Depends on `/bin/sh`, `sed`, and `grep`. Used by build/version extraction paths.

Risks: Unquoted `$1` can be word-split or glob-expanded. Multiple `git` tokens can produce multi-line output. The parser accepts any token containing `git`, not just structured version metadata.

Test signals: Paths with `git<sha>`, no git marker, multiple git-like segments, and whitespace.
