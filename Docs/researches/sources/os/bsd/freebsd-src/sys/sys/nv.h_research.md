# File Research: sources/os/bsd/freebsd-src/sys/sys/nv.h

This header declares the FreeBSD nvlist public API for name/value lists. It includes the opaque base type from `<sys/_nv.h>`, and in userland pulls in standard bool, integer, stdio, varargs, and namespace-renaming support.

It defines maximum name length, all supported value type numbers, and nvlist flags for case-insensitive lookup and non-unique names. The API covers lifecycle and error state (`nvlist_create`, `destroy`, `error`, `empty`, `flags`, `set_error`, `clone`), diagnostic dumps in userland, packed-size calculation, pack/unpack, socket send/recv/xfer, iteration, parent/array linkage queries, and existence checks by type.

For each supported type, the API provides add, append-to-array, move/consume, get, take/remove-and-return, and free operations. Types include null, bool, number, string, nested nvlist, binary, arrays of those core types, and userland-only descriptor/descriptors arrays. The distinction between `add` and `move` is important: add copies caller-provided data while move consumes caller-owned buffers or descriptors.

Filesystem and kernel relevance comes from structured control-plane data exchange. Nvlists are used by facilities that need extensible typed parameters across kernel/user or subsystem boundaries without adding a new fixed struct for every revision.
