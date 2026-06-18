# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/istack.h

Declares the expandable ref-stack interface and `ref_stack_block` layout. It describes how Ghostscript’s principal interpreter stacks are represented as linked array blocks and how guard regions are included in the containing arrays.

Exports initialization, expansion control, error-code setup, maximum count and margin setters, count/index/counttomark helpers, store checking and storing, pop/clear operations, block pop, extension, push, block enumeration, GC cleanup, release, and free.

Also defines convenience macros such as `ref_stack_count_inline`, `ref_stack_max_count`, `ref_stack_clear`, and `ref_stack_pop_to`.
