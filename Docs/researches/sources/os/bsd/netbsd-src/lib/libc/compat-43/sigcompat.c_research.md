# File Research: sources/os/bsd/netbsd-src/lib/libc/compat-43/sigcompat.c

## Scope

Implements 4.3BSD signal compatibility functions on top of modern `sigaction`, `sigprocmask`, and `sigsuspend`.

## APIs And Behavior

- Converts between `struct sigvec` and `struct sigaction` with `sv2sa()` and `sa2sv()`.
- `sigvec()` delegates to `sigaction()`, preserving old mask/flag layout.
- `sigsetmask()` sets the signal mask and returns the previous low-word mask.
- `sigblock()` blocks requested signal bits and returns the previous low-word mask.
- `sigpause()` builds a signal set from an integer mask and calls `sigsuspend()`.

## Dependencies And Invariants

- Includes `<compat/sys/signal.h>` for old `sigvec` definitions.
- Uses only `sa_mask.__bits[0]`, so this is intentionally limited to the old integer signal-mask ABI.
- Flips `SV_INTERRUPT` with modern restart semantics using xor conversion.
