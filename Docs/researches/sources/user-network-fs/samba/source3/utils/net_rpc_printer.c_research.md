# sources/user-network-fs/samba/source3/utils/net_rpc_printer.c

## Purpose

`net_rpc_printer.c` contains the implementation behind the `net rpc printer` subcommands registered from `net_rpc.c`: listing printers, listing drivers, publishing/unpublishing printer objects in Active Directory through spoolss, and migrating printer queues, drivers, forms, settings, and security descriptors from a remote print server to a destination server.

## Important APIs, Types, and Functions

The file mixes SMB file-copy helpers and Spoolss RPC wrappers. `net_copy_fileattr()` copies security descriptors, DOS attributes, and timestamps through `cli_ntcreate()`, `cli_query_secdesc()`, `cli_qfileinfo_basic()`, `cli_set_secdesc()`, and `cli_setfileinfo_ext()`. `net_copy_file()` copies file contents or creates directories over connected SMB shares, then delegates metadata preservation to `net_copy_fileattr()`. `net_copy_driverfile()`, `check_arch_dir()`, and `copy_print_driver_3()` handle print driver file layout under `print$\<architecture>\<version>\file`.

The `net_spoolss_*` wrappers normalize common spoolss calls: enumerate/open/get/set printers, set printer data, enumerate keys/data/forms/drivers, get driver info, and add drivers. Higher-level exported internals include `rpc_printer_list_internals()`, `rpc_printer_driver_list_internals()`, publish helpers, and the five migration functions: security, forms, drivers, printers, and settings.

## Control Flow

Listing and publishing use `get_printer_info()` to either enumerate all local/shared printers or open one named printer. Publishing opens each printer with `PRINTER_ALL_ACCESS`, fetches level 7 data, changes the action to publish/update/unpublish, and calls `SetPrinter`.

Migration functions first connect to the destination spoolss pipe via `connect_dst_pipe()`, enumerate source printers, and iterate over the selected printer set. Security migration opens matching source and destination printer handles, reads the source level 3 security descriptor, copies it into destination level 2 info, and calls `SetPrinter`. Forms migration enumerates source forms and adds only `SPOOLSS_FORM_PRINTER` forms on the destination. Driver migration opens source and destination `print$` shares, enumerates architecture table entries, fetches source driver level 3, copies each driver file to the destination architecture directory, calls `AddPrinterDriver`, and finally sets the destination printer's driver name. Printer migration creates missing destination queues from source `PRINTER_INFO_2` using `rpccli_spoolss_addprinterex()`. Settings migration copies devmode/selected level 2 attributes, republishes if needed, enumerates legacy printer data and subkey values, rewrites location-sensitive registry values such as port, UNC name, server name, and short server name, and writes them with `SetPrinterData` or `SetPrinterDataEx`.

## State and Persistence

Persistent state is remote print server state: printer queues, driver files under `print$`, forms, printer registry data, Active Directory publication state, and security descriptors. Local state is only transient talloc allocations, SMB file handles, and RPC policy handles. File copy operations can create destination files and directories and can partially populate `print$` before an RPC add-driver operation fails.

## Dependencies and Integration Points

The implementation depends on generated Spoolss RPC stubs, `rpc_client/cli_spoolss.h`, SMB client helpers from `libsmb`, `nt_printing.h`, registry value helpers, security descriptor utilities, `archi_table`, and command glue in `net_rpc.c`. It also uses `connect_dst_pipe()` and `connect_to_service()` from the broader net utility code to reach a destination server and its `print$` share.

## Risks

Migration is multi-step and not transactional; a failure can leave copied driver files, created forms, or queues without matching settings. Several paths abort the whole migration on one printer failure, while others continue on form add failures, so behavior is uneven. Driver file path parsing assumes `...\<short_arch>\<version>\<filename>` and does not robustly handle malformed dependent-file paths. `net_copy_fileattr()` closes handles explicitly and again in cleanup if `fnum_src` or `fnum_dst` remain nonzero. In settings migration, the inner `for (i=0; keylist && keylist[i] != NULL; i++)` reuses the outer printer loop variable, which can skip printers or terminate the outer loop incorrectly. The polling loop in `watch_service_state` equivalent does not exist here; spoolss operations generally rely on immediate RPC results.

## Test Signals

High-value tests are integration-style: enumerate printers/drivers against a known server, migrate a fixture printer queue to a disposable destination, verify copied `print$` files and driver registration, copy forms while ignoring built-ins, copy security descriptors, and compare printer data subkeys after settings migration. A focused regression test should exercise settings migration with more than one printer and at least one subkey to catch loop-index corruption.
