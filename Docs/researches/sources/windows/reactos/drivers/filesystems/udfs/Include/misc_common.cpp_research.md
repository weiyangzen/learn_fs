# File Research: sources/windows/reactos/drivers/filesystems/udfs/Include/misc_common.cpp

Tiny shared helper module for UDF volume modified-state bookkeeping.

Key responsibilities:
- Implements `UDFSetModified()` to increment `Vcb->Modified` and normalize overflow/sign-bit cases back to `2`.
- Implements `UDFPreClrModified()` to set `Vcb->Modified` to `1` before clearing.
- Implements `UDFClrModified()` to log the clear operation and decrement `Vcb->Modified`.

Important behavior:
- Uses `UDFInterlockedIncrement()` and `UDFInterlockedDecrement()` wrappers, which may be real interlocked operations or simple increments depending on build environment.
- The modified state is a counter-like field rather than a simple boolean.

Dependencies:
- Depends on `PVCB` containing a `Modified` field.
- Uses `UDFPrint()` and environment interlocked macros.

Notable risks:
- In user-mode shim builds, the interlocked macros in `env_spec_w32.h` are simple non-atomic increments/decrements, so concurrent callers would not get real atomicity there.
