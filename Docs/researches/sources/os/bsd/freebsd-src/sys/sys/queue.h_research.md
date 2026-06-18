# File Research: sources/os/bsd/freebsd-src/sys/sys/queue.h

Read completely: 1097 lines.

## Purpose
Defines FreeBSD's intrusive linked-list macro library: singly-linked lists, singly-linked tail queues, doubly-linked lists, and tail queues.

## Main Elements
- Documents operation availability and complexity for SLIST, STAILQ, LIST, and TAILQ.
- Supports optional queue macro debug tracing, pointer trashing, and structural assertions; kernel `INVARIANTS` can enable assertions automatically.
- Defines C and C++ head/entry variants for each queue family.
- SLIST supports head/entry declaration, initialization, empty/first/next access, forward and safe iteration, O(n) concatenation/removal, prevptr removal, split, swap, and atomic-empty reads.
- STAILQ supports head/tail insertion, concatenation, last lookup, forward/safe iteration, remove/split/swap/reverse, and tail invariant checks.
- LIST supports O(1) arbitrary removal/replacement via back-pointers, before/after/head insertion, forward/safe iteration, previous lookup, split, swap, and structural checks.
- TAILQ supports head/tail/before/after insertion, forward/reverse/safe iteration, fast last/previous lookup variants, concatenation, removal/replacement, split, swap, tracing, and structural checks.
- Provides `_EMPTY_ATOMIC` helpers using atomic pointer loads for all queue families.

## Dependencies And Integration
Used throughout the kernel and userland headers as the basic intrusive container facility. Depends on `sys/cdefs.h`, `__containerof`, optional atomics, panic/abort behavior for debug assertions, and consumer-provided element fields.

## Risk Notes
Macros assume correct intrusive field ownership and external synchronization. Removing or reusing elements incorrectly can corrupt lists; debug modes help catch bad prev/next/tail links but alter layout when tracing is enabled.
