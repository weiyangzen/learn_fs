# File Research: sources/windows/reactos/drivers/filesystems/udfs/Include/env_spec_w32.cpp

Win32/native-mode implementation side of the UDF environment shim used by user-mode formatter/browser/library builds.

Key responsibilities:
- Defines global Win32-side open/lock state when not building the formatter state object: `LockMode`, `open_as_device`, and `opt_invalidate_volume`.
- Optionally loads a skin/UI plugin DLL through `SkinLoad()`, calls its exported `SkinInit`, and initializes the returned `SKIN_API`.
- Routes physical device control through `UDFPhSendIOCTL()`, either to Win32 `DeviceIoControl()` or to LIBUDF/LIBUDFFMT callback tables.
- Implements synchronous physical reads and writes through Win32 file handles or callback hooks.
- Provides image/file helpers: `set_image_size()`, `get_file_size()`, and `set_file_pointer()`.
- Implements `my_open()` for opening a target as a volume/device first, locking it, enabling extended DASD I/O, and falling back to an image file.
- Provides volume lock/unlock helpers using UDF private lock IOCTLs where available and standard `FSCTL_LOCK_VOLUME` / `FSCTL_UNLOCK_VOLUME` otherwise.
- Provides `udf_lseek64()`, formatter size probing callback glue, device-type detection, debug console output, Win32 time conversion wrappers, optional thread-local heaps, kernel-like pool allocation wrappers, and `ProbeMemory()`.

Important behavior:
- `UDFPhWriteSynchronous()` aligns writes through a temporary 64 KiB-aligned buffer before `WriteFile()` in the non-library Win32 path.
- `my_open()` retries locking and can issue `FSCTL_INVALIDATE_VOLUMES` or `IOCTL_UDF_INVALIDATE_VOLUMES` after enabling `SE_TCB_NAME`.
- If direct volume opening or locking fails in Win32 mode, `my_open()` falls back to creating/opening the provided name as a plain image file and marks the target as disk-like.
- Drive type detection treats two-character `X:` names as devices and warns about `X;`.
- `ProbeMemory()` touches the last byte and every page, optionally writing back the same value, under SEH to validate user pointers.
- Native mode includes `env_spec_nt.cpp` at the end, extending this file with NT-native implementations.

Dependencies:
- Uses Win32 APIs such as `CreateFileW`, `DeviceIoControl`, `SetFilePointer`, `ReadFile`, `WriteFile`, `GetVolumeInformationW`, `GetDriveTypeW`, and privilege APIs.
- Depends on UDF-specific structures and callbacks including `PVCB`, `UDFWriteData`, `PUDF_VOL_HANDLE_I`, `_UDF_FMT_PARAMETERS`, and UDF private IOCTL values.
- Uses declarations/macros from `env_spec_w32.h`, `nt_native.h` in native builds, `string_lib.cpp`, and optionally `env_spec_nt.cpp`.

Notable risks:
- Several paths cast pointers and offsets through `ULONG`, so the code is effectively 32-bit-oriented despite using 64-bit file offsets.
- The volume open/lock retry logic has many build-flag-dependent branches; behavior differs substantially between normal tools, LIBUDF, LIBUDFFMT, CDRW_W32, and NT native builds.
- `SkinLoad()` does not free the DLL on partial initialization failure.
- Thread heap free paths return without releasing `MemLock` if the current thread pool is not found.
