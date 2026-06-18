# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ostack.h

Defines macros for Ghostscript’s operand stack as seen by operator implementations. It maps the current interpreter context to `o_stack`, `osp`, `osbot`, and `ostop`, and provides push/pop/overflow/underflow helpers.

The important design note is that the interpreter does not pre-check underflow before invoking an operator. Guard refs below the operand stack allow normal type checks to detect underflow later; operators that do not type-check or that have variable arity must call `check_op`.

Dependencies include `iostack.h` and `icstate.h`. The stack itself is a linked block stack, so whole-stack operators must account for non-contiguous storage.

This is interpreter runtime support, unrelated to Plan 9 filesystem behavior.
