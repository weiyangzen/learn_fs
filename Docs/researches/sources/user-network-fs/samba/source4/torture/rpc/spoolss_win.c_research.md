# sources/user-network-fs/samba/source4/torture/rpc/spoolss_win.c

## Purpose

`spoolss_win.c` reproduces a Windows XP-style sequence of spoolss RPCs. It validates printer/server open patterns, buffer retry behavior, printer data queries, printer enumeration, job/form/driver/key enumeration, and handle close ordering as observed from Windows clients.

## Important APIs, Types, and Functions

`struct test_spoolss_win_context` holds enumeration results, the current `GetPrinter` output, printer keys, and whether the selected printer has a driver. `test_OpenPrinterEx()` and `test_OpenPrinterAsAdmin()` centralize `OpenPrinterEx` calls. Data and enumeration helpers include `test_GetPrinterData()`, `test_EnumPrinters()`, `test_GetPrinter()`, `test_EnumJobs()`, `test_GetPrinterDriver2()`, `test_EnumForms()`, `test_EnumPrinterKey()`, and `test_EnumPrinterDataEx()`. The single scenario is `test_WinXP()`, registered by `torture_rpc_spoolss_win()`.

## Control Flow

`test_WinXP()` opens the print server with an XP-like read/admin/execute sequence, validates selected server printer-data values, enumerates printers with initial and retry buffers, and skips printer-specific checks when no printer exists. When a printer is present, it opens multiple handles with different access masks, calls `GetPrinter` at levels 0, 2, and 7 with varying offered sizes, checks `EnumJobs`, optional driver lookup, forms, printer registry keys, and data under each key. The test intentionally interleaves open and close calls to mirror real client behavior.

## State and Persistence Behavior

The test is designed to be non-mutating. It opens and closes spoolss handles and queries server/printer state, but it does not set printer data or modify jobs. State is held in talloc contexts and policy handles. A failure before later close calls may leak remote handles until the server connection is torn down.

## Dependencies and Integration Points

The file depends on generated spoolss client stubs, common torture RPC registration, `test_ClosePrinter()`, Samba loadparm context, `dcerpc_server_name()`, and server printer/driver configuration. It uses registry-like spoolss key/data APIs and Windows NT x86 driver architecture strings.

## Risks and Edge Cases

Behavior is intentionally tied to Windows XP traces, so modern Windows or Samba behavior can diverge. The suite tolerates absent printers by skipping deep checks, which reduces coverage in minimal environments. `GetPrinterDriver2` is only required to succeed when `GetPrinter` level 2 reports a driver name. Printer key enumeration stores pointers into returned NDR buffers, so context lifetime matters. Several hard-coded expected values, such as `MajorVersion == 3`, `W3SvcInstalled == 0`, and error codes for `UISingleJobStatusString`, are compatibility assumptions.

## Test Signals

The strongest signal is `testWinXP` completing against a configured print server with at least one printer. Useful sub-signals are correct insufficient-buffer retries, stable printer name round-trips, key/data enumeration, and clean close behavior across many handles.
