# File Research: sources/windows/reactos/drivers/filesystems/udfs/Include/env_spec_w32.h

User-mode and NT-native compatibility header that lets shared UDF code build outside the real kernel DDK environment.

Key responsibilities:
- Selects either `nt_native.h` or Win32 headers depending on `NT_NATIVE_MODE`.
- Defines NT-like primitive types, constants, status helpers, pool types, IRQL values, events, resources, spin locks, device objects, packets, FCB headers, section object pointers, time fields, and I/O status blocks.
- Provides debug, user-print, timing, performance, allocation, dump, assertion, breakpoint, and validation macros.
- Defines the `SKIN_API` interface and maps skin/UI printing and command-line access for skinned and non-skinned builds.
- Maps `ExAllocatePool`, `ExAllocatePoolWithTag`, and `ExFreePool` either to Win32 `GlobalAlloc`/`GlobalFree` or to implementations in `env_spec_w32.cpp`.
- Implements resource/spin-lock wrappers over `AcquireXLock()` and simple interlocked counter macros for non-CDRW builds.
- Declares physical I/O functions, image helpers, open/exit helpers, volume locking helpers, device type lookup, and memory probing.
- Provides fallback list-manipulation macros if the platform headers do not define them.

Important behavior:
- Debug and user output behavior changes under `DBG`, `PRINT_ALWAYS`, `PRINT_TO_DBG_LOG`, `CDRW_W32`, `LIBUDFFMT`, and `LIBUDF`.
- Resource acquisition macros spin around `AcquireXLock()` and treat shared and exclusive acquisition the same way.
- `DEVICE_OBJECT` is a local substitute whose fields differ depending on LIBUDF/LIBUDFFMT/non-library builds.
- `UDFPhWriteVerifySynchronous` is currently aliased to `UDFPhWriteSynchronous`; the real verify implementation is disabled in the `.cpp`.
- `KeDelayExecutionThread()` maps to `NtDelayExecution()` in native mode and `Sleep()` in normal Win32 mode.

Dependencies:
- Includes `platform.h` and `udferr_usr.h`, plus `env_spec_nt.h` in native mode.
- Expects shared UDF code to provide `AcquireXLock`, `MyRtlCompareMemory`, string helpers, and UDF structures such as `_UDFVolumeControlBlock`.
- Declarations match implementations in `env_spec_w32.cpp`.

Notable risks:
- This header intentionally redefines or substitutes many kernel APIs; incorrect build flags can silently select very different semantics.
- Several macros evaluate arguments more than once or expand to statement blocks without `do { } while (0)`, so caller syntax matters.
- Pointer arithmetic macros and some structure substitutions assume 32-bit pointer sizes.
- The `write()` prototype here omits the `PVCB` argument present in the non-formatter `.cpp` implementation, suggesting it is protected by build configurations rather than a universal interface.
