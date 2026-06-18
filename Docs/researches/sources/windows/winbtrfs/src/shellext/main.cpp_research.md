# File Research: sources/windows/winbtrfs/src/shellext/main.cpp

Read status: complete, 780 lines.

This file is the shell extension DLL core. It owns COM class IDs, DLL exports, registry registration, shared formatting/error helpers, command-line parsing, and simple rundll helpers for creating subvolumes and snapshots.

COM and DLL behavior:
- Defines CLSIDs for icon overlay, context menu, file property sheet, and volume property sheet.
- `DllCanUnloadNow` returns `S_OK` when global `objs_loaded` is zero.
- `DllGetClassObject` allocates `Factory`, assigns the requested factory type, and returns the requested factory interface.
- `DllRegisterServer` writes CLSID and shell-extension registry keys for icon overlay, context menus, file/folder property sheets, and drive property sheets.
- `DllUnregisterServer` removes those keys with an in-file recursive `reg_delete_tree` implementation.
- `DllInstall` delegates to register/unregister.
- `DllMain` stores the module handle on process attach.

Shared helpers:
- `set_dpi_aware` dynamically loads `SetProcessDpiAwareness` from `shcore.dll`.
- `format_size` produces localized byte and larger-unit strings with locale grouping.
- `load_string` loads string resources into `std::wstring`.
- `wstring_sprintf` formats wide strings with `_vsnwprintf`.
- `format_message` and `format_ntstatus` convert Win32 and NTSTATUS failures to text.
- UTF-8/UTF-16 conversion helpers support exception messages.
- `string_error`, `last_error`, and `ntstatus_error` wrap localized or system errors for use across the shell extension.
- `error_message` displays localized error message boxes.
- `command_line_to_args` wraps `CommandLineToArgvW`.

Rundll helper exports:
- `CreateSubvolW` parses command-line args and creates a Btrfs subvolume at the requested path using `FSCTL_BTRFS_CREATE_SUBVOL`.
- `CreateSnapshotW` parses source and destination arguments and creates a snapshot using `FSCTL_BTRFS_CREATE_SNAPSHOT`.

Integration:
- Central dependency for all files in this group through `shellext.h` declarations and global `module`.
- Registers the COM classes implemented by `factory.cpp`, `iconoverlay.cpp`, `contextmenu.cpp`, `propsheet.cpp`, and volume property-sheet code outside this group.

Risk and maintenance notes:
- Registry writes use `HKEY_CLASSES_ROOT` and `HKEY_LOCAL_MACHINE`, so registration requires appropriate privileges.
- The custom recursive registry delete is needed for older systems but must be treated carefully because it deletes whole subtrees.
- `wstring_sprintf` uses varargs and `_vsnwprintf`; format-string/resource mismatches can surface as runtime formatting errors.
- Some rundll helper creation paths silently return on failures instead of surfacing errors.
