# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/list.h

## Role

Public intrusive doubly-linked list API for illumos kernel/user common code.

## Structure

Includes `list_impl.h`, typedefs opaque `list_node_t` and `list_t`, and declares create/destroy, insert/remove, move, head/tail, next/prev, empty test, link initialization/replacement, and active-link test functions.

## Dependencies And Consumers

The implementation layout comes from `list_impl.h`. Consumers embed `list_node_t` in their own objects and initialize a `list_t` with object size and node offset.

## Important Details

This is an intrusive list API: objects own their link node, and the list knows only the node offset. The header declares functions only; locking, if needed, is the caller's responsibility.

## Research Notes

Read completely: 65 lines, 1843 bytes.
