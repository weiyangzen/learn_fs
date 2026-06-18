# File Research: sources/os/plan9/9front/sys/src/9/kw/arch.c

Provides miscellaneous ARM architecture process/register helpers.

Key elements:
- Builds kernel `Ureg` snapshots for sleeping processes.
- Enforces aligned user addresses for system calls that require them.
- Returns the user PC from the last debug register frame.
- Allows devproc register writes while preserving protected PSR mode/interrupt bits.
- Sets initial kernel process PC/SP.
- Saves/restores floating-point process state.
- Identifies user-mode exception frames.
- Implements interrupt-masked 32-bit compare-and-swap.

Dependencies:
- Uses ARM PSR constants from `arm.h` and FPU helpers from platform code.

Research notes:
- The CAS implementation is uniprocessor-style: it raises interrupt priority and then issues `coherence` after a successful store.
