# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/ldo.h

## Role

`ldo.h` declares the internal stack and call-control API.

## Main Responsibilities

- Defines stack growth helpers and pointer save/restore macros used across reallocations.
- Defines the protected function callback type `Pfunc`.
- Declares protected parsing, hooks, pre-call/post-call, direct calls, protected calls, stack reallocation/growth/shrink, non-local throws, and protected execution.

## Integration Points

This header is used by API, debug, lexer/parser, memory, object, and VM code that can grow stacks, run protected operations, or throw errors.

## Risk Notes

`savestack` and `restorestack` encode stack pointers as byte offsets. Misusing them with non-stack pointers would corrupt call recovery after stack reallocations.
