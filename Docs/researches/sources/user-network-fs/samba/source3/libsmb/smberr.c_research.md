# sources/user-network-fs/samba/source3/libsmb/smberr.c

Purpose: `smberr.c` maps legacy SMB DOS error classes/codes to human-readable names and maps Unix errno values to Win32 `WERROR`. It is a support module for diagnostics and error translation in SMB client code.

Important APIs and data: static `err_code_struct` arrays define DOS (`ERRDOS`), server (`ERRSRV`), and hard (`ERRHRD`) error names/messages. `err_classes` maps class bytes such as `0x01`, `0x02`, `0x03`, and `0xFF` to class names and optional message tables. Exported functions are `smb_dos_err_name(uint8_t e_class, uint16_t num)`, `get_dos_error_msg(WERROR result)`, `smb_dos_err_class(uint8_t e_class)`, and `map_werror_from_unix(int error)`.

Control flow: `smb_dos_err_name` scans `err_classes`, then scans the matching table for the numeric error. If not found in a known class, it returns a talloc-stack string containing the numeric code; if the class is unknown, it returns a talloc-stack string naming the unknown class/code. `get_dos_error_msg` extracts the low WERROR value and resolves it under `ERRDOS`. `smb_dos_err_class` scans class mappings and formats unknown classes similarly. `map_werror_from_unix` delegates Unix-to-NTSTATUS mapping to `map_nt_error_from_unix` and then converts to WERROR via `ntstatus_to_werror`.

State and persistence: no persistent state. Fallback strings are allocated on `talloc_tos()`, so callers must not assume static lifetime for unknown-code returns.

Dependencies and integration: depends on Samba's legacy SMB error constants, NTSTATUS/WERROR mapping helpers, and talloc stack context. It integrates with client diagnostics and any code that still reports SMB1 DOS class/code errors.

Risks: the table is partial and legacy-oriented; consumers needing precise Windows error text should not treat these strings as exhaustive. Fallback allocations assert non-null, so out-of-memory can abort in those rare paths. Since messages in table entries are currently unused by exported functions, updating message text alone may not affect visible output.

Test signals: unit tests should verify known mappings across ERRDOS/ERRSRV/ERRHRD, unknown code formatting in known classes, unknown class formatting, `get_dos_error_msg` behavior for representative WERRORs, and Unix errno mapping parity with NTSTATUS conversion.
