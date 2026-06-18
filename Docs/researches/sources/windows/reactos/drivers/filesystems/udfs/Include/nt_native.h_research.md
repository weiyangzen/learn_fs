# File Research: sources/windows/reactos/drivers/filesystems/udfs/Include/nt_native.h

Large native NT API compatibility header used when building UDF tools for `NT_NATIVE_MODE`.

Key responsibilities:
- Includes low-level NT headers and storage/device IOCTL headers, then fills in many NT user/kernel declarations normally provided by Win32/DDK headers.
- Defines object forward declarations, access masks, generic rights, file rights, file attributes, share modes, create dispositions, create/open options, file status return values, alignment constants, device characteristics, and FSCTL values.
- Declares RTL registry query structures/constants and string/integer conversion routines.
- Declares ANSI/Unicode string manipulation, conversion, comparison, append, free, and memory helper routines.
- Defines `TIME_FIELDS` and declares time conversion routines.
- Defines generic mapping, `CTL_CODE`, method/access constants, `IO_STATUS_BLOCK`, APC callback type, file information classes and structures, filesystem information classes, and registry key/value structures.
- Declares native registry APIs: `NtEnumerateKey`, `NtOpenKey`, `NtQueryValueKey`, `NtSetValueKey`, and `NtDeleteValueKey`.
- Defines object-manager, directory, symbolic-link, section, memory protection/allocation, process, thread, client ID, floating-save-area, x86 context, registry value type, environment/startup, and heap structures/constants.
- Declares native process/thread/display/heap/file/device-control/read/write/query/set/close/wait/delay APIs.

Important behavior:
- The file is declaration-only; it makes native-mode code compile without the normal Win32 process environment.
- It targets x86 context layout explicitly through `CONTEXT_i386`, `FLOATING_SAVE_AREA`, and register fields.
- Some definitions are guarded for ReactOS or existing header symbols, but many constants are unconditional compatibility copies.
- It maps user-mode style names such as `BOOL`, `DWORD`, and `LPVOID` to NT primitive types.

Dependencies:
- Includes `<excpt.h>`, `<ntdef.h>`, `<ntstatus.h>`, `<string.h>`, `<DEVIOCTL.H>`, `<NTDDSTOR.H>`, and `<NTDDDISK.H>`.
- Used by `env_spec_w32.h` and `env_spec_w32.cpp` when `NT_NATIVE_MODE` is set.
- Assumes NT declarations/macros such as `NTSYSAPI`, `NTAPI`, `POBJECT_ATTRIBUTES`, `UNICODE_STRING`, `PSTRING`, and `LARGE_INTEGER` are available from included NT headers.

Notable risks:
- This header duplicates many platform definitions; conflicts are likely if included alongside newer or fuller SDK/DDK headers.
- The context and pointer-related declarations are 32-bit/x86-centric.
- Several declarations are historical and may not match modern NT header signatures exactly.
