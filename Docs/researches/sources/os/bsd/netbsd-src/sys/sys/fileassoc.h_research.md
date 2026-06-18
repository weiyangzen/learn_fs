# File Research: sources/os/bsd/netbsd-src/sys/sys/fileassoc.h

Read completely: 53 lines.

## Purpose
Declares per-vnode/per-mount file association tables for attaching subsystem-private data to files.

## Main Interfaces
- Opaque `fileassoc_t` and callback types.
- Registration: `fileassoc_register`, `fileassoc_deregister`.
- Lookup and mutation: `fileassoc_lookup`, `fileassoc_add`, `fileassoc_clear`.
- Cleanup: `fileassoc_table_delete`, `fileassoc_table_clear`, `fileassoc_file_delete`.
- Iteration callback: `fileassoc_table_run`.

## Dependencies And Integration
Uses mount and vnode objects. Consumers can associate metadata with vnodes without changing filesystem node structures.

## Risks And Edge Cases
- Cleanup callbacks must be correct because data lifetime is tied to vnode and mount teardown.
- Associations depend on vnode identity stability.

## Filesystem Relevance
High. Used for filesystem-adjacent metadata such as veriexec or security state associated with vnodes.
