# sources/user-network-fs/samba/source3/printing/nt_printing_migrate.c

Purpose: converts records from legacy NT printing TDB blobs into current winreg-backed spoolss data by unmarshalling historical NDR structures and invoking winreg spoolss RPC helpers.

Important APIs and functions: `printing_tdb_migrate_form()` unmarshals `ntprinting_form` and calls `winreg_printer_addform1()`, skipping built-in forms and treating existing forms as success. `printing_tdb_migrate_driver()` unmarshals `ntprinting_driver`, strips path components from driver files, populates `spoolss_AddDriverInfo3`, and calls `winreg_add_driver()`. `printing_tdb_migrate_printer()` unmarshals `ntprinting_printer`, maps `ntprinting_printer_info` and devmode fields into `spoolss_SetPrinterInfo2` plus `spoolss_DeviceMode`, then updates printer data values with `winreg_set_printer_dataex()`. `printing_tdb_migrate_secdesc()` unmarshals `sec_desc_buf` and applies it with `winreg_set_printer_secdesc()`.

Control flow: callers provide one key/value pair from old TDB storage. The function selects the expected NDR structure, optionally enables ASCII string conversion for old data, translates fields into spoolss structures, and returns `NTSTATUS` derived from NDR or WERROR failures. Printer data migration splits stored names at the first backslash into key and value names.

State and persistence: this file does not open databases itself. It writes migrated state to the registry-style printing store through the winreg pipe and does not delete source TDB records. It preserves driver private data and devmode extra data when present.

Dependencies and integration: uses generated NDR parsers for `ntprinting`, `spoolss`, and security descriptors, plus `rpc_pipe_client` binding handles and `cli_winreg_spoolss` helpers. It is called by `nt_printing_migrate_internal.c` while walking old `ntdrivers.tdb`, `ntprinters.tdb`, and `ntforms.tdb`.

Risks: malformed blobs currently map to `NT_STATUS_NO_MEMORY`, which can obscure parse corruption. `printing_tdb_migrate_printer()` mutates `printer_data[j].name` in place while splitting on `\\`. Field-by-field devmode translation is easy to regress if generated structs change. Tests should feed representative legacy blobs, built-in forms, existing forms, missing devmode, driver paths with backslashes, invalid NDR, and printer data with and without backslash separators.
