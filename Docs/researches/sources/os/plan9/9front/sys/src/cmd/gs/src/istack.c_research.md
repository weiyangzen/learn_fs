# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/istack.c

Implements expandable stacks of Ghostscript refs, used by the operand, execution, and dictionary stacks. Each stack is a linked list of `t_array` blocks whose leading refs encode `ref_stack_block` metadata, followed by guard slots, used refs, unused refs, and optional top guards.

The file handles initialization, guard setup, max count and margin management, counting, indexing across blocks, count-to-mark, VM-space store checks, copying stack contents to arrays with save/write barriers, popping, pushing, extending, block split/merge, enumeration, GC cleanup, and release/free.

It is GC-aware: the stack object has custom mark/relocate procedures, and block unused areas are nulled to avoid stale GC roots. Store operations enforce local/global/system/foreign VM-space rules through `refs_check_space` and `ref_assign_old/new`.
