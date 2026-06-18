# sources/security-integrity/selinux/checkpolicy/queue.h

## Purpose

`queue.h` declares the generic queue abstraction used by the SELinux checkpolicy parser. It defines the node and queue structures and the operations implemented in `queue.c`.

## Important Types and APIs

`queue_element_t` is `void *`, allowing the parser to store strings and NULL list separators. `queue_node_t` stores one element plus the next pointer. `queue_info_t` stores head and tail pointers, and `queue_t` is a pointer to that structure.

The API supports creation, tail insertion, head insertion, removal, peeking, clearing, destruction, mapping, and conditional removal during mapping.

## Control Flow and Integration

The parser calls `queue_insert()` for normal token order and `queue_push()` for grammar productions that need reverse-order name construction. Semantic functions consume with `queue_remove()` and occasionally inspect the next item with `queue_head()`.

## State and Persistence Behavior

The header exposes the internal structure rather than making `queue_t` opaque, so callers could inspect or mutate internals directly. In practice the parser uses the functions. The implementation treats stored elements as owned by the queue when clearing/destroying.

## Dependencies and Risks

There are no external dependencies. The main risk is ownership ambiguity caused by a generic `void *` queue and public structs. Callers must not put stack pointers or string literals into a queue that may be cleared or destroyed.

## Test Signals

Compile and unit tests should confirm API consistency with `queue.c`, especially head/tail updates and NULL element support.
