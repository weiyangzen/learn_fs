# File Research: sources/os/bsd/freebsd-src/sys/sys/_sigset.h

Signal set bit layout.

Key elements:
- Defines signal set sizing and bit-indexing macros.
- Defines `_SIG_MAXSIG` as 128 and `_SIG_WORDS` as 4.
- Defines `__sigset_t` as four 32-bit words.
- Under kernel 4.3 compatibility, defines `osigset_t`.

Dependencies:
- Requires `__uint32_t` from included type context.

Research notes:
- Establishes ABI layout for signal masks used in process, thread, and ucontext state.
