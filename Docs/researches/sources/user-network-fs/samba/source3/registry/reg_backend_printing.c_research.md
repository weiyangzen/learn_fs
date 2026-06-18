# sources/user-network-fs/samba/source3/registry/reg_backend_printing.c

## Purpose
`reg_backend_printing.c` implements a virtual registry view for printer data. It maps accesses under `HKLM\SYSTEM\CURRENTCONTROLSET\CONTROL\PRINT\PRINTERS` onto Samba's stored Windows NT printer registry path `HKLM\SOFTWARE\MICROSOFT\WINDOWS NT\CURRENTVERSION\PRINT\PRINTERS`.

## Important APIs, Types, And Functions
The central type is the local `struct reg_dyn_tree`, a dispatch row containing a normalized path and optional fetch/store callbacks for subkeys and values. `printing_ops` exports the backend through `registry_ops`. `create_printer_registry_path()` normalizes an input key and, for the control-printers tree, builds the corresponding WinNT-printers path. `match_registry_path()` finds the best matching dispatch row in `print_registry[]`.

## Control Flow
Public registry operations enter `regprint_fetch_reg_keys()`, `regprint_store_reg_keys()`, `regprint_fetch_reg_values()`, or `regprint_store_reg_values()`. Each resolves the input key to a `print_registry[]` index. The only active row targets `KEY_CONTROL_PRINTERS` and routes through `key_printers_*()`, which either translate the requested subpath or fall back to the WinNT printers root. Missing callbacks produce failure for stores/fetch-subkeys and zero values for fetch-values on an otherwise matched key.

## State And Persistence
This backend does not own persistent state. Reads and writes are delegated to `regdb_ops` against the normalized WinNT printer key. It therefore presents an alternate registry namespace over data persisted by the default registry database backend.

## Dependencies And Integration Points
It depends on `registry.h`, `reg_util_internal.h`, path constants from the registry layer, and `regdb_ops`. `reg_init_full.c` installs `printing_ops` under `KEY_PRINTING "\\Printers"` while other printing-related paths remain directly backed by `regdb_ops`.

## Risks And Test Signals
Ordering in `print_registry[]` matters because the first prefix match wins. Tests should cover root printer enumeration, nested printer paths, writes through the control path reflecting in the WinNT path, path normalization and separator variants, and unknown paths returning `-1`/`False`. The translation helper uses normalized prefix checks but slices the original `key`; mixed-case or unusual slash inputs should be included in tests.
