# sources/user-network-fs/nfs-utils/support/include/conffile.h

## Purpose
Declares a section/key configuration parser interface used by nfs-utils daemons and support helpers.

## Important APIs, Types, and Functions
`struct conf_list_node`, `struct conf_list`, `conf_begin/end`, getters for strings, bools, numbers, sections, lists, addresses, mutation/write helpers, `conf_cleanup()`, `modified_by`, and inline `upper2lower()`.

## Control Flow
Callers initialize a config file, query section/key values through typed getters, optionally write/remove entries, report state, and cleanup. List results use TAILQ-backed nodes.

## State and Persistence Behavior
Parser state is owned by the implementation. Returned strings/lists generally require caller cleanup via documented functions. Config files are persistent external state.

## Dependencies and Integration Points
Depends on BSD queue macros, stdio, ctype, fixed-width types, and socket address declarations. Used by `nfsd_path.c` for `exports.rootdir` and other daemon config consumers.

## Risks and Edge Cases
Ownership rules vary by getter, and config changes can affect chroot/rootdir behavior globally. `upper2lower()` stops on `tolower(*str) == 0`, so input must be NUL-terminated.

## Test Signals
Test typed lookup defaults, missing sections, list cleanup, address parsing, writes/removes, base64 decode, and mixed-case normalization.
