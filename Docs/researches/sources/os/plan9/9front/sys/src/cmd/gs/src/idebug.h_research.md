# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/idebug.h

Declares interpreter debugging helpers.

Key points:
- Declares name/ref/packed-ref print functions.
- Declares single-ref, ref-region, array, and stack dump functions.
- Forward-declares `ref_stack_t` when needed.

Research notes:
- This header is only useful in debug-oriented code paths that can include interpreter ref types.
