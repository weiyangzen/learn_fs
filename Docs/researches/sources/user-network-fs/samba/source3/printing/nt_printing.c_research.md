# sources/user-network-fs/samba/source3/printing/nt_printing.c

## Purpose
`nt_printing.c` implements major source3 NT spoolss printer support: initialization of print driver directories/databases, driver architecture/version cleanup, PE/NE version parsing, driver file promotion into `print$` download directories, driver/file in-use checks, driver file deletion, printer access checks, print time checks, and winreg-backed printer add/remove helpers.

## Important APIs, types, and functions
- `nt_printing_init` creates required print driver directories, upgrades printing TDBs, registers driver-upgrade forwarding, and checks published printers in ADS mode.
- `get_short_archi` maps Windows architecture strings to Samba short architecture directory names via `archi_table`.
- `get_file_version`, `handle_pe_file`, and `handle_ne_file` parse DOS/PE/NE executable version resources from uploaded driver files.
- `file_version_is_newer` compares old/new driver files by version resource when available, otherwise by modification time.
- `clean_up_driver_struct` and `clean_up_driver_struct_level` normalize spoolss add-driver structures, strip client paths, handle `APD_COPY_FROM_DIRECTORY`, validate architecture, and determine `cversion`.
- `move_driver_to_download_area` and `move_driver_file_to_download_area` copy uploaded driver files into `print$/<arch>/<version>/`.
- `printer_driver_in_use` and `printer_driver_files_in_use` query winreg driver/printer data to decide whether a driver or its files can be removed.
- `delete_driver_files` unlinks unused files from the print driver download directory.
- `print_access_check`, `print_time_access_check`, `nt_printer_remove`, and `nt_printer_add` enforce printer/job permissions, schedule windows, and maintain winreg printer records.

## Control flow
Initialization starts by ensuring `print$` architecture directories, package-aware subdirectories, color directory, and state `DriverStore` directories exist. It then upgrades printing TDB state, registers `MSG_PRINTER_DRVUPGRADE` forwarding to the background queue daemon, and checks AD-published printers when in ADS security mode.

Driver installation first cleans the submitted spoolss structure. Paths such as `c:\...`, `.\...`, or UNC upload paths are reduced to basenames; a temporary driver directory is extracted for copy-from-directory installs; architecture strings are mapped; and `get_correct_cversion` opens the uploaded driver file as the requesting session to infer kernel/user-mode driver version. `move_driver_to_download_area` then opens a connection to `print$`, becomes the session user, creates the target `<short_arch>/<version>` directory, and copies the driver, data, config, help, and unique dependent files when `file_version_is_newer` says the uploaded copy should replace the current one.

Version detection reads DOS headers, seeks to PE/NE headers, scans PE section tables for `.rsrc`, scans version-resource signatures, and extracts major/minor fields. If version data is unavailable, file replacement falls back to mtime comparison. Driver deletion first requires external checks that the driver and files are not in use, then opens `print$` as the session user and unlinks each referenced file. Access checks short-circuit root and `SE_PRINT_OPERATOR`, otherwise fetch printer security descriptors from winreg, map generic rights, derive child job descriptors when needed, and call `se_access_check`.

## State and persistence behavior
Persistent state is spread across filesystem directories under `print$`, Samba state `DriverStore`, printing TDB upgrade state, winreg printer/driver records, and AD-published printer metadata. This file mutates filesystem contents by creating directories, copying driver files, and deleting files. It mutates messaging registrations at runtime and reads printer security/time windows from winreg-backed printer info.

## Dependencies and integration points
The file depends on printing TDB helpers, queue process messaging, generated spoolss/netlogon structures, spoolss server utilities, secrets/machine SID/security helpers, smbd connection/VFS APIs, auth/session code, winreg spoolss client helpers, global messaging contexts, and time utilities. It is central to RPC spoolss add/delete printer driver flows and to SMB access to the `print$` share.

## Risks and edge cases
- PE/NE parsing handles untrusted uploaded driver files and uses many offset/size calculations; integer wrap checks are present but this remains a sensitive parser.
- Driver installation can leave partial updates if one file is copied and a later file fails, as noted by an in-code comment.
- `move_driver_file_to_download_area` takes a `uint32_t version` parameter but checks `version == -1`; this sentinel is awkward and easy to misuse.
- Version fallback to mtime can install older binary content if timestamps are misleading.
- Deletion ignores individual unlink errors and returns true once attempted, so callers may need independent cleanup verification.
- Access checks depend on winreg security descriptor retrieval; failure maps to memory/error outcomes rather than nuanced authorization status.
- Operations that become the user and operate through VFS must preserve correct impersonation cleanup on every error path.

## Test signals
Important tests include initialization with and without a `print$` share, architecture mapping for all entries, PE/NE version extraction on fixtures with and without version info, replacement decisions by version and mtime, add-driver cleanup for level 3/6/8 and `APD_COPY_FROM_DIRECTORY`, partial-copy error injection, driver/file in-use checks against mocked winreg data, delete attempts on shared dependent files, root/print-operator/DACL access checks, and time-window allow/deny behavior.
