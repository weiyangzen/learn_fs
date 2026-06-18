# sources/storage-engines/wiredtiger/tools/tcmalloc/define-with_tcmalloc.sh

Purpose: defines a shell helper function that runs commands with the workspace's built `libtcmalloc.so` preloaded.

Important APIs and control flow: intended to be sourced, not executed. It finds the git top level, checks `${TOP__}/TCMALLOC_LIB/libtcmalloc.so`, then uses `eval` to define `with_tcmalloc() { LD_PRELOAD=$SO__:$LD_PRELOAD "$@"; }`, and unsets temporary variables.

State and persistence behavior: mutates the current shell by defining `with_tcmalloc`. It does not write files.

Dependencies and integration points: pairs with `build-tcmalloc.sh` output. It depends on Git and dynamic linker `LD_PRELOAD` behavior.

Risks: `if ! [[ $? ]]; then` does not robustly test `git rev-parse` failure because `$?` is numeric and non-empty; however command substitution failure may still leave unusable paths. `LD_PRELOAD=$SO__:$LD_PRELOAD` can introduce a trailing empty path component. `return` requires sourcing; executing the script directly from a shell may produce return errors.

Test signals: after sourcing from a repo with `TCMALLOC_LIB/libtcmalloc.so`, `type with_tcmalloc` should show the function and `with_tcmalloc env` should include the shared library in `LD_PRELOAD`.
