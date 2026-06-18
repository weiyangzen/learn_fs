# sources/security-integrity/selinux/checkpolicy/queue.c

## Purpose

`queue.c` implements a small singly linked, double-ended queue used by the checkpolicy parser to shuttle token text and NULL separators from grammar productions to semantic action functions. Although generic in type (`void *` elements), its primary role here is managing dynamically allocated identifier strings.

## Important APIs and Functions

`queue_create()` allocates an empty queue. `queue_insert()` appends an element to the tail. `queue_push()` prepends an element to the head. `queue_remove()` pops and returns the head element. `queue_head()` returns the head element without removing it. `queue_clear()` frees all nodes and their elements but keeps the queue object. `queue_destroy()` frees all nodes/elements and the queue itself.

`queue_map()` applies a callback to each element and stops on nonzero callback status. `queue_map_remove_on_error()` applies a callback and removes elements for which the callback returns nonzero, invoking a second callback on removed elements.

## Control Flow

All mutation functions first handle NULL queue pointers. Insert/push allocate a node and update head/tail consistently. Remove frees only the node, not the returned element. Clear and destroy free both node and element, assuming element ownership belongs to the queue at that time.

## State and Persistence Behavior

The queue persists until `queue_destroy()`. Elements inserted into the parser queue are usually heap-allocated strings from `insert_id()` or NULL separators. Ownership transfers out on `queue_remove()`; callers must free non-NULL returned elements or insert them into policydb-owned structures.

## Dependencies and Integration Points

The implementation depends only on `<stdlib.h>` and `queue.h`. It is used by `policy_define.c`, `parse_util.c`, and `module_compiler.c` as the parser's identifier transport.

## Risks and Edge Cases

Because `queue_clear()` and `queue_destroy()` blindly call `free(p->element)`, the queue is safe only for heap pointers or NULL when those functions are used. It is not thread-safe. `queue_map_remove_on_error()` does not free elements itself; it delegates element cleanup to `g`, then frees the node. Parser correctness depends on preserving insertion order and allowing NULL separators.

## Test Signals

Tests should cover empty operations, append order, push order, mixed push/insert behavior, remove head/tail transitions, clear/destroy with NULL elements, map early-stop behavior, and map-remove tail/head updates.
