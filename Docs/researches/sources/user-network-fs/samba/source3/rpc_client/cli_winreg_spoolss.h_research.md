# sources/user-network-fs/samba/source3/rpc_client/cli_winreg_spoolss.h

## Purpose
`cli_winreg_spoolss.h` exposes the spoolss-over-winreg helper API implemented by `cli_winreg_spoolss.c`. It is the public contract used by Samba's spoolss server, print migration, and printing subsystems to store and retrieve printer configuration through the winreg RPC pipe.

## Important APIs, Types, And Functions
The header defines `enum spoolss_PrinterInfo2Mask`, a bitmask describing which fields in `spoolss_SetPrinterInfo2` should be written by `winreg_update_printer()`, plus `SPOOLSS_PRINTER_INFO_ALL`. It declares functions for printer lifecycle, printer info, security descriptors, arbitrary data values, subkey enumeration/deletion, change ID update/read, forms, driver metadata, driver lists, core drivers, and driver packages.

Important declarations include `winreg_create_printer()`, `winreg_update_printer()`, `winreg_get_printer()`, `winreg_get/set_printer_secdesc()`, `winreg_get/set_printserver_secdesc()`, `winreg_set/get/enum/delete_printer_dataex()`, `winreg_enum/delete_printer_key()`, `winreg_printer_*form1()`, `winreg_add/get/del_driver()`, `winreg_get_driver_list()`, `winreg_add/get_core_driver()`, and `winreg_add/get/del_driver_package()`.

## Control Flow
The header has no runtime control flow. It organizes the exported registry-backed operations into a stable C interface that accepts `TALLOC_CTX`, `dcerpc_binding_handle`, printer/share names, generated spoolss structures, and output pointers. Callers are expected to own the RPC binding and pass talloc contexts for returned structures.

## State And Persistence
The header declares functions that mutate persistent registry state but does not hold state itself. Its bitmask constants control selective persistence of `PRINTER_INFO_2` fields.

## Dependencies And Integration Points
It includes `replace.h` and generated `spoolss.h`, forward-declares `struct dcerpc_binding_handle`, and is included by spoolss server utility code, print migration code, and registry-backed printing helpers.

## Risks
The bitmask values are ABI-like local contracts with the implementation. Adding `PrinterInfo2` fields or changing mask values without updating `winreg_update_printer()` can silently drop or miswrite state. Documentation in the header has minor typos, but the function prototypes are the important contract.

## Test Signals
Compile coverage catches signature drift. Behavioral tests should cover each exported operation through spoolss server wrappers, especially selective `info2_mask` updates, security descriptor defaulting, dataex operations, form builtin handling, and driver/package persistence.
