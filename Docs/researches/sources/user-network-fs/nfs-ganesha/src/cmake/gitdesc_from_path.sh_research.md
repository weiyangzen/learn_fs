# sources/user-network-fs/nfs-ganesha/src/cmake/gitdesc_from_path.sh

Purpose: Extracts a git description fragment from a path-like input, used by build/version tooling.

Important APIs/types/functions: Shell pipeline assigns `res` by stripping everything through `_desc_` and removing a trailing `-[0-9]*.[0-9]*.[0-9]*` pattern; prints `NO-GIT` when empty, otherwise prints the result.

Control flow: One positional argument is transformed through `sed`; output is a single line.

State and persistence behavior: Stateless shell utility; no files are modified.

Dependencies and integration points: Depends on `/bin/sh` plus `sed`. Likely called from CMake/version scripts when deriving metadata from generated archive paths.

Risks: `$1` is unquoted in `echo $1`, so whitespace, glob characters, or leading options can be mangled. Pattern matching is specific to archive naming conventions and may return unexpected strings if `_desc_` appears multiple times.

Test signals: Inputs with no desc, with `_desc_<hash>-1.2.3`, with spaces, and with unusual suffixes.
