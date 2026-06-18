# Research: sources/user-network-fs/samba/source4/torture/rpc/spoolss.c

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-009992`: lines 1-8667, `Docs/researches/chunks/subset-b-009992_research.md`
- `subset-b-009993`: lines 8668-11725, `Docs/researches/chunks/subset-b-009993_research.md`

## Chunk Research

### subset-b-009992: lines 1-8667

# sources/user-network-fs/samba/source4/torture/rpc/spoolss.c lines 1-8667

## Purpose

This chunk is the first, large part of Samba's `smbtorture` RPC test coverage for the MS-SPOOLSS print spooler interface. It builds a torture-suite harness around a live `spoolss` DCE/RPC pipe, opens a print-server handle, discovers the server's spooler architecture, enumerates server resources, opens and creates printers, mutates printer configuration, exercises job submission, and cross-checks spooler state against the remote registry service.

The code is test code rather than production spooler implementation. Its value is in encoding protocol expectations: successful and failing `WERROR` values, buffer-resizing behavior, level-specific structure equivalence, security descriptor and devmode persistence, registry layout compatibility, printer data key semantics, and server-specific skip/relaxation rules for Samba, Windows versions, and unsupported RPC operations.

The requested chunk ends at line 8667 inside `torture_rpc_spoolss_printer_setup_common()`, immediately after it decides whether to use an existing XPS driver or upload a local CUPS/Adobe-style driver. Driver upload/removal implementation and the final suite registration live after this chunk.

## Important Types and Context

- `struct test_spoolss_context` is the common print-server test fixture. It stores the `spoolss_pipe`, server architecture string, server `policy_handle`, and cached enumeration results for ports, drivers, monitors, print processors, and printers across levels.
- `struct torture_driver_context` describes local and remote driver directories/environments plus a level-8 `spoolss_AddDriverInfo8` record. The first chunk initializes this for printer fixture setup but relies on later-file helpers for complete upload/removal behavior.
- `struct torture_printer_context` is the per-printer fixture. It tracks the spoolss pipe, level-2 printer add/set info, associated driver context, mode flags (`ex`, `wellknown`), whether a driver was added or found, optional devmode, and the opened printer handle.
- Comparison and sizing macros (`COMPARE_*`, `CHECK_NEEDED_SIZE_*`, `CHECK_ALIGN`, `DO_ROUND`) implement repeated assertions across info levels and NDR-computed byte sizes. The size checks are guarded by the `spoolss_check_size` torture setting.
- Registry key constants (`TOP_LEVEL_PRINT_*`, `TOP_LEVEL_CONTROL_*`) encode expected Windows registry paths for print server, printers, forms, environments, and drivers.

## RPC and Helper API Coverage

The chunk covers these SPOOLSS RPC surfaces:

- Server and printer handles: `OpenPrinter`, `OpenPrinterEx`, `ClosePrinter`, secondary authenticated close behavior, bad-name handling, and server-handle `GetPrinter`/`SetPrinter` level rules.
- Enumeration APIs: `EnumPorts`, `EnumPrinterDrivers`, `EnumMonitors`, `EnumPrintProcessors`, `EnumPrintProcessorDataTypes`, `EnumPrinters`, `EnumForms`, `EnumJobs`, `EnumPrinterData`, `EnumPrinterDataEx`, `EnumPrinterKey`, and `EnumPerMachineConnections`.
- Directory and driver discovery: `GetPrintProcessorDirectory`, `GetPrinterDriverDirectory`, `GetPrinterDriver2`, `GetCorePrinterDrivers`, and `GetPrinterDriverPackagePath`.
- Printer metadata mutation: `SetPrinter` for normal fields, control commands, security descriptors, devmodes, rename behavior, c_setprinter observation, and `ChangeID`.
- Forms: `GetForm`, `AddForm`, `SetForm`, `DeleteForm`, with print-server and printer-handle variants.
- Jobs: `StartDocPrinter`, `StartPagePrinter`, `WritePrinter`, `EndPagePrinter`, `EndDocPrinter`, `GetJob`, `SetJob`, `AddJob`, and named job property APIs.
- Printer data and key-value storage: `GetPrinterData`, `SetPrinterData`, `DeletePrinterData`, `GetPrinterDataEx`, `SetPrinterDataEx`, `DeletePrinterDataEx`, and `DeletePrinterKey`.
- Printer and driver provisioning: `AddPrinter`, `AddPrinterEx`, `DeletePrinter`, well-known printer list behavior, and initial setup for printer driver fallback.
- Print processor and per-machine connection management: `AddPrintProcessor`, `DeletePrintProcessor`, `AddPerMachineConnection`, `DeletePerMachineConnection`.

It also uses WINREG RPC (`OpenHKLM`, `OpenKey`, `CloseKey`, `QueryValue`) as an independent observation channel for spooler state.

## Control Flow

The top-level setup path for non-printer server tests is:

1. `torture_rpc_spoolss_setup_common()` opens an RPC connection to `ndr_table_spoolss`.
2. `test_OpenPrinter_server()` opens the server pseudo-printer using `\\server` and stores `server_handle`.
3. `test_get_environment()` reads `Architecture` via `GetPrinterData` and stores the environment string.
4. Server tests use the shared context and close the server handle through `torture_rpc_spoolss_teardown_common()`.

Most enumeration helpers follow the same two-call pattern: call once with no buffer or zero offered size, expect `WERR_INSUFFICIENT_BUFFER` or `WERR_MORE_DATA`, allocate the returned `needed` size, call again, assert `WERR_OK`, then optionally compare the returned size against local NDR sizing. Examples include `EnumPorts`, `EnumPrinterDrivers`, `EnumMonitors`, `EnumPrinters`, `GetPrinter`, `GetForm`, `EnumForms`, `GetJob`, `EnumJobs`, `GetPrinterData`, `GetPrinterDataEx`, and winreg `QueryValue`.

Cross-level tests use the highest or richest level as the reference:

- `EnumPorts` compares level 1 names against level 2 names.
- `EnumPrinterDrivers` compares levels 1, 2, 3, 4, 5, and 6 to level 8 where fields overlap.
- `EnumMonitors` compares level 1 to level 2 and verifies level-2 `environment`.
- `EnumPrinters` compares levels 0, 1, 4, and 5 to level 2 where practical.
- `GetPrinter` iterates levels 0-8 and, when level 2 names a driver, probes `GetPrinterDriver2` for that driver.

Printer-handle tests flow through `call_OpenPrinterEx()` and `test_existing_printer_openprinterex()`: open a printer, test SDs, info levels, forms, form registry mirrors, printer data enumeration, key enumeration, pause/resume, real print job creation/deletion, data set/get/delete matrices, optional secondary close rejection, and finally close the handle.

Printer creation setup begins in `torture_rpc_spoolss_printer_setup_common()`: initialize a driver record, set `LPT1:` as the target port, fill remote printserver metadata, derive a local driver directory for the architecture, prefer installed "Microsoft XPS Document Writer" or v4 drivers, otherwise attempt driver upload from `/usr/share/cups/drivers`.

## State and Persistence Behavior

This chunk intentionally mutates spooler state and then checks persistence or cleanup:

- `test_SetPrinter_errors()` checks command and info-level error surfaces for zeroed `SetPrinter` inputs, including printer control commands and invalid levels.
- `test_PrinterInfo()` encodes a broad field persistence matrix for level 2, 4, 5, and 6 printer fields, including expected errors for unknown ports, drivers, separator files, and print processors. It is currently skipped with `torture_skip()`, but the intended coverage remains documented in code.
- `test_PrinterInfo_SD()` saves the original security descriptor, runs level-2/level-3 equivalence and set/get tests, adds many ACEs to stress SD size/round-trip behavior, then restores the original descriptor.
- `test_PrinterInfo_DevMode()` saves the original global devmode, compares level 8 and level 2, mutates copies/form name through level 8 and level 2 setters, tests individual public devmode fields, probes `OpenPrinterEx` devmode behavior, then restores the original devmode.
- Forms are added, verified through spoolss and optionally winreg, updated by `SetForm`, found via enumeration, and deleted. Duplicate adds and deleting built-in/invalid forms have expected error codes.
- Print jobs are created by full document/page/write/end flows, then enumerated, fetched, renamed through `SetJob` level 1, paused/resumed, and finally deleted. A separate matrix sets, retrieves, enumerates, and deletes named job properties for string, int32, int64, byte, and blob property types.
- Printer data tests write values under `PrinterDriverData` and arbitrary subkeys using multiple registry types, verify spoolss and winreg consistency, enumerate both legacy and Ex views, and delete values/keys afterward.
- `test_ChangeID()` verifies that `ChangeID` is identical through `GetPrinterData`, `GetPrinterDataEx`, and `GetPrinter` level 0, does not change for read-only operations, and increases after `SetPrinter` mutations.
- `test_printer_rename()` renames a printer via level-2 `SetPrinter`, validates the new name, conditionally checks old-name lookup failure on non-Samba servers, opens by the new name, and leaves later cleanup to the fixture.
- `test_csetprinter()` creates a second printer to observe `info0.c_setprinter` before and after add/open operations, then closes and deletes the new printer.
- `test_set_printer_printserverhandle()` mutates the print-server security descriptor by adding an ACE for a fixed SID, verifies it appears, removes it, and verifies it is gone.

Cleanup is generally inline and assertion-driven. If a mid-test assertion aborts, residual state is possible: test forms, printer data keys, print jobs, added printers, per-machine connections, or modified security/devmode state may remain unless surrounding torture teardown later handles it.

## Registry Integration

The winreg helpers provide a second view of spooler persistence:

- `test_winreg_OpenHKLM()`, `test_winreg_OpenKey[_opts]()`, `test_winreg_CloseKey()`, and `test_winreg_QueryValue()` wrap WINREG RPC with the same buffer-resize idiom.
- `test_winreg_symbolic_link()` checks that `SYSTEM\\CurrentControlSet\\Control\\Print\\Printers` is a registry symbolic link to the Software print-printer path on non-Samba targets.
- `test_GetPrinterInfo_winreg()` compares `GetPrinter` level 2 fields against values under both Control and Software printer keys, including strings, DWORDs, binary devmode, and binary security descriptor.
- `test_GetPrintserverInfo_winreg()` compares print-server level-3 SD to `ServerSecurityDescriptor`.
- `test_GetDriverInfo_winreg()` compares driver info levels 8, 6, and 3 to registry driver keys, including stripped file basenames, dates, versions, multi-string fields, and Windows-version-specific binary date/version handling.
- `test_PrintProcessors()` verifies that enumerated print processors have corresponding environment registry keys.
- `test_PrinterData_winreg()`, `test_Forms_winreg()`, `test_PrinterInfo_winreg()`, `test_PrintserverInfo_winreg()`, `test_DriverInfo_winreg()`, and `test_PrintProcessors_winreg()` open a separate winreg pipe, run the consistency check, close HKLM, and free the pipe.
- `test_PrinterData_DsSpooler()` verifies that `SetPrinter` level-2 fields are reflected under the printer's `DsSpooler` key as REG_SZ/REG_DWORD data.

## Dependencies and Integration Points

The file depends on Samba's generated NDR/RPC bindings for SPOOLSS, WINREG, security descriptors, and helper libraries:

- Generated RPC/NDR headers: `ndr_spoolss.h`, `ndr_spoolss_c.h`, `ndr_winreg_c.h`, `ndr_security.h`, `ndr_misc.h`.
- DCE/RPC and torture framework: `torture/rpc/torture_rpc.h`, `torture/torture.h`, `torture/ndr/ndr.h`.
- Security helpers: `security_descriptor_equal`, ACL equality, SID parse/create, `security_descriptor_dacl_add/del`.
- Registry value helpers: `push_reg_sz`, `pull_reg_sz`, `push_reg_multi_sz`, `pull_reg_multi_sz`, `reg_val_data_string`, `str_regtype`.
- Client and transport helpers: `dcerpc_server_name`, secondary auth connection, SMB/SMB2 includes for later driver/file work.
- Talloc memory management and Samba utility routines such as `data_blob_talloc_zero`, `data_blob_string_const`, `generate_random_buffer`, `strlen_m_term`, `IVAL`, `SIVAL`, `SBVAL`, and `push_nttime`.

The tests are tightly integrated with live server capabilities and torture settings:

- `samba3`, `samba4`, `w2k3`, and `dangerous` settings change expectations, skip behavior, or destructive-operation protection.
- `spoolss_check_size` enables local NDR size validation for returned buffers.
- `NCACN_NP` transport is required for the secondary-pipe close rejection test.
- Local filesystem availability of `/usr/share/cups/drivers` influences whether setup can upload a fallback driver.

## Risks and Edge Cases

- Many tests depend on real spooler state and can be flaky against servers with no printers, missing XPS drivers, unsupported levels, unusual registry layouts, or restricted permissions.
- The file has several server-specific relaxations and skips; protocol behavior differs between Samba, Windows Server versions, and NT4-like servers.
- `test_EnumPrinterData_consistency()` assumes `EnumPrinterData` and `EnumPrinterDataEx` use compatible ordering for value names.
- `test_DeletePrinterKey()` can wipe printer registry keys when passed an empty key name, guarded by the `dangerous` setting.
- `test_PrinterInfo()` is currently skipped despite containing broad persistence expectations, so regressions in those fields may not be caught unless the skip is removed.
- Some helpers use fixed names (`torture_value*`, `torturedataex`, `testform_*`, `SAMBA smbtorture Test Printer (Copy 2)`, `torture_printer*`) and may collide with leftover state from prior failed runs.
- The printer setup path may delete an existing printer with the same torture name before retrying add; that is expected for cleanup of prior runs but risky if names collide with non-test objects.
- Devmode and security descriptor tests deliberately modify global printer state and restore it afterward; aborting between mutation and restore can leave changed printer defaults or ACLs.
- Job tests create multiple print jobs and expect deletion to work. Servers that actually print jobs quickly or apply queue policies may produce timing-sensitive results.
- Driver and package APIs may return `HRESULT` values mapped through `WIN32_FROM_HRESULT`, unlike most tests that assert `WERROR` directly.

## Test Signals

Strong positive signals:

- First-call insufficient-buffer or more-data paths report correct `needed` sizes, second calls succeed, and optional NDR size checks match.
- Enumeration counts match across comparable levels, and shared fields are equal across levels.
- `GetPrinterData`, `GetPrinterDataEx`, `EnumPrinterData`, `EnumPrinterDataEx`, and winreg views agree on type, size, and bytes.
- Security descriptors and devmodes round-trip between levels 2/3 and 2/8 respectively, including larger modified descriptors and driverextra devmode data.
- `ChangeID` is stable on reads and increases after real `SetPrinter` mutation.
- Added forms, printer data values, job properties, per-machine connections, and temporary printers can be observed and then deleted.
- Invalid inputs return the encoded expected errors, including `WERR_INVALID_LEVEL`, `WERR_INVALID_PARAMETER`, `WERR_INVALID_PRINTER_NAME`, `WERR_UNKNOWN_PORT`, `WERR_UNKNOWN_PRINTER_DRIVER`, `WERR_UNKNOWN_PRINTPROCESSOR`, `WERR_INVALID_ENVIRONMENT`, `WERR_FILE_EXISTS`, `WERR_NO_MORE_ITEMS`, and HRESULT success/failure for core driver APIs.

Weak or conditional signals:

- `test_PrinterInfo()` is skipped, so its detailed field persistence matrix is documentation until re-enabled.
- Some checks warn instead of failing where Windows/Samba behavior differs or historic behavior is unclear.
- Later suite registration and complete printer teardown are outside this chunk, so this research covers setup and helper behavior but not all final test-case wiring.

### subset-b-009993: lines 8668-11725

# sources/user-network-fs/samba/source4/torture/rpc/spoolss.c lines 8668-11725

## Chunk Scope

This chunk is part of Samba's RPC torture coverage for the `spoolss` interface. It starts in the tail of printer fixture setup, covers printer teardown and most per-printer torture tests, registers the `spoolss` and `spoolss.printer` suites, then defines the printer-driver add/delete/upload test helpers and the `spoolss.driver` suite. It is not production spooler code; it is integration-test code that drives real DCE/RPC `spoolss`, `winreg`, SMB1, and SMB2 operations against a target server and checks Windows-compatible behavior.

The chunk depends on local context defined earlier in the file, especially `struct test_spoolss_context`, `struct torture_printer_context`, `struct torture_driver_context`, the `TORTURE_*` printer/driver names, and helper wrappers such as `test_OpenPrinter_server`, `test_EnumJobs_args`, `test_DoPrintTest*`, `test_PrinterInfo*`, `test_SetPrinterDataEx*`, `test_DriverInfo_winreg`, and `test_EnumPrinterDrivers_findone`.

## Purpose

The first half validates behavior of printers created by `AddPrinter` and `AddPrinterEx`: job creation, job enumeration, purge, security descriptors, devmode persistence, registry-backed printer information, printer data keys/values, DsSpooler values, GDI printer information contexts, bidirectional data calls, publish/unpublish state, Branch Office job logging, and server OS version reporting.

The second half validates printer driver lifecycle semantics: querying the driver directory, uploading candidate driver files over SMB, calling `AddPrinterDriver` and `AddPrinterDriverEx` at levels 1, 2, 3, 4, 6, and 8, verifying driver registry state through `winreg`, deleting drivers with normal and extended delete APIs, and checking whether associated driver files remain or are removed according to delete flags.

## Important Types, APIs, and Helpers

- `struct torture_printer_context`: fixture state for printer tests. This chunk reads `spoolss_pipe`, `info2`, `driver`, `ex`, `wellknown`, `added_driver`, `have_driver`, `devmode`, and `handle`.
- `struct torture_driver_context`: fixture state for driver tests. This chunk fills local and remote environments/directories, `spoolss_AddDriverInfo8`, and the `ex` selector for `AddPrinterDriverEx` versus `AddPrinterDriver`.
- `struct test_spoolss_context`: print-server fixture state, used here by `test_printserver_info_winreg`.
- `spoolss` RPC calls used directly in this chunk include `CreatePrinterIC`, `PlayGDIScriptOnPrinterIC`, `DeletePrinterIC`, `SendRecvBidiData`, `LogJobInfoForBranchOffice`, `GetPrinterDriverDirectory`, `AddPrinterDriver`, `AddPrinterDriverEx`, `DeletePrinterDriver`, and `DeletePrinterDriverEx`.
- Wrapper tests used by this chunk include printer open/close, pause/resume, purge, print job creation, job enumeration, printer info/security/devmode checks, registry checks, and driver enumeration.
- SMB dependencies are split by purpose: `smb2_connect`, `torture_smb2_testfile`, `smb2_util_write`, and `smb2_util_close` test spooling through a printer share, while `smbcli_full_connection`, `smbcli_mkdir`, `smbcli_open`, `smbcli_write`, `smbcli_unlink`, and `smbcli_close` upload, verify, and remove driver files in the print driver share.
- NDR and binary helpers include `ndr_pull_spoolss_OSVersion`, `data_blob_*`, `IVAL`, `CVAL`, `SVAL`, `GUID_from_string`, `GUID_string2`, and NT time comparison helpers.

## Printer Fixture Flow

`torture_rpc_spoolss_printer_setup`, `torture_rpc_spoolss_printerex_setup`, `torture_rpc_spoolss_printerwkn_setup`, and `torture_rpc_spoolss_printerexwkn_setup` allocate a `torture_printer_context`, set whether `AddPrinterEx` and well-known-printer modes should be used, set the printer name, and delegate to `torture_rpc_spoolss_printer_setup_common` from the preceding chunk. The common setup path may upload and register a printer driver before adding the test printer. The well-known printer setup variants currently call `torture_skip` before delegating, so the level-1 well-known add paths are intentionally disabled.

`torture_rpc_spoolss_printer_teardown_common` reverses the fixture. For non-well-known printers it deletes the opened printer, re-enumerates local printers, and asserts the name is gone. If setup added a driver, teardown first removes uploaded driver files with `remove_printer_driver`, then also calls `DeletePrinterDriverEx` with `DPD_DELETE_ALL_FILES`. Teardown deliberately warns rather than immediately failing on driver cleanup errors after the printer-delete phase, because leaked test driver files should be reported but should not hide the primary cleanup path. The public teardown wrapper frees the fixture with `talloc_free`.

## Printer Test Control Flow

Most printer test entry points are thin fixture-aware wrappers registered by `torture_tcase_printer`. They fetch the `torture_printer_context`, obtain `p->binding_handle`, and call lower-level helpers with assertions:

- `test_print_test`, `test_print_test_extended`, and `test_print_test_properties` pause the printer, create or inspect jobs, and resume it. The extended test downgrades a failure to skip for Samba3 targets. The properties test skips Samba3 and Samba4 targets.
- `test_print_test_smbd` connects to static printer share `print1` over SMB2, creates a file named `smbd_spooler_job`, writes payload bytes, then verifies `EnumJobs` over `spoolss` can see a job with that document name. It intentionally avoids dynamically added printers because different spoolss worker processes may observe the new printer at different times.
- `test_print_test_purge` pauses the printer, creates eight jobs, asserts the queue length is eight, purges the printer, asserts the queue is empty, and resumes.
- `test_printer_sd`, `test_printer_dm`, `test_printer_info_winreg`, `test_printer_change_id`, `test_printer_keys`, `test_printer_data_consistency`, `test_printer_data_keys`, `test_printer_data_values`, `test_printer_data_set`, `test_printer_data_winreg`, and `test_printer_data_dsspooler` delegate to earlier helper coverage for printer security descriptors, devmode, registry synchronization, change IDs, key enumeration, data enumeration, and data mutation.
- `test_printer_ic` skips Samba targets, creates a printer information context, probes `PlayGDIScriptOnPrinterIC` with undersized buffers expecting `WERR_NOT_ENOUGH_MEMORY`, then succeeds with a 4-byte font-count buffer and again with enough space for all `UNIVERSAL_FONT_ID` entries before deleting the GDI handle.
- `test_printer_bidi` skips Samba targets, verifies an arbitrary BIDI action returns `WERR_NOT_SUPPORTED`, and only continues to schema enumeration if the printer has `PRINTER_ATTRIBUTE_ENABLE_BIDI`.
- `test_printer_publish_toggle` reads levels 7 and 2, then toggles publish state through `SetPrinter` level 7. Its helpers validate both level-2 `PRINTER_ATTRIBUTE_PUBLISHED` and level-7 action/GUID behavior, including pending publish/unpublish states.
- `test_print_job_enum` purges first, verifies level 1 and 2 enumeration on an empty queue, verifies invalid level 100 returns `WERR_INVALID_LEVEL`, creates eight jobs, repeats the enumeration assertions, deletes each job, and resumes.
- `test_printer_log_jobinfo` directly calls `LogJobInfoForBranchOffice` with zero, one, and forty-two branch-office job-data entries, expecting invalid parameter for an empty container and success for populated containers.
- `test_printer_os_versions` compares `GetPrinter` level 0 version bytes with the server's `OSVersion` printer data value decoded as `spoolss_OSVersion`.

## Suite Registration

`torture_tcase_printer` is the shared per-printer test registrar. It adds open-printer, set-printer, print-job, printer-info, security descriptor, devmode, registry, change-id, printer-data, driver-registry, rename, GDI IC, BIDI, publish-toggle, job enumeration, branch-office job logging, and OS-version tests to an existing `torture_tcase`.

`torture_rpc_spoolss_printer` creates the `printer` suite and adds separate fixture cases for `addprinter`, `addprinterex`, `addprinterwkn`, and `addprinterexwkn`. Only the normal and Ex cases get the full `torture_tcase_printer` registration in this chunk; well-known cases are fixture-created but skipped by setup.

`torture_rpc_spoolss` creates the top-level `spoolss` suite. It registers many print-server tests from earlier chunks under a `printserver` tcase and then adds the printer suite. This is the integration point that makes the printer fixture tests part of the public spoolss torture suite.

## Driver Add/Delete Helpers

`test_GetPrinterDriverDirectory_getdir` implements the common two-call "query needed buffer, then retry" pattern for `GetPrinterDriverDirectory` level 1 and returns the directory name when requested.

`get_driver_from_info` and `get_environment_from_info` normalize `spoolss_AddDriverInfoCtr` levels into driver name and architecture strings for logging. They support levels 1, 2, 3, 4, 6, and 8, matching the add-driver matrix in this chunk.

`test_AddPrinterDriver_exp` and `test_AddPrinterDriverEx_exp` are direct RPC wrappers that assert NT transport success and compare the returned `WERROR` to the caller's expected result. Level-specific helpers build the relevant `spoolss_AddDriverInfo*` structure:

- Level 1 is expected to fail with `WERR_INVALID_LEVEL` even after `driver_name` is set.
- Level 2 progressively fills required fields and expects `WERR_INVALID_PARAMETER` until `config_file` is present, then expects success. For `AddPrinterDriverEx`, a zero flag call near the end is still expected to be invalid.
- Levels 3 and 4 are supported by both normal and Ex APIs and verify that enumerated paths begin with the remote driver directory when a reference directory is supplied.
- Levels 6 and 8 are only valid for `AddPrinterDriverEx`; normal `AddPrinterDriver` should return `WERR_INVALID_LEVEL`. For Ex, the tests verify enumeration, path prefixes, driver date, and driver version.

`test_DeletePrinterDriver_exp` and `test_DeletePrinterDriverEx_exp` wrap the delete RPCs. `test_DeletePrinterDriver` and `test_DeletePrinterDriverEx` add behavioral checks around them: deletion with environment `FOOBAR` must fail with `WERR_INVALID_ENVIRONMENT`, deletion with the real environment must succeed, subsequent enumeration should not find the driver, and a second delete must return `WERR_UNKNOWN_PRINTER_DRIVER`.

`test_PrinterDriver_args` is the central add/delete matrix dispatcher. It calls the level-specific add helper, skips deletion for level 1 and for non-Ex level 6/8 cases, opens a separate `winreg` pipe, checks driver registry state via `test_GetDriverInfo_winreg`, and then deletes with the matching normal or Ex delete helper.

## Driver File and Directory Flow

`fillup_printserver_info` opens the print server, obtains the remote server environment, closes the handle, then fetches the print driver directory for either the requested local environment or the discovered remote environment. This populates `d->remote.environment` and `d->remote.driver_directory`.

`driver_directory_dir` returns the final path component after the last backslash in a driver directory. `driver_directory_share` parses a UNC path to extract the SMB share name. `CREATE_PRINTER_DRIVER_PATH` builds a full remote path under a temporary upload directory.

`create_printer_driver_directory` optionally creates a per-test upload directory under the remote architecture directory. `upload_printer_driver_file` maps a possibly path-qualified driver file to a local file under `d->local.driver_directory`, opens the remote destination, streams local bytes in 64,512-byte chunks, and closes the remote handle. `upload_printer_driver` connects to the driver share, optionally creates the upload directory, and uploads driver, data, config, help, and dependent files.

`check_printer_driver_file` verifies a copied driver file in the versioned destination directory `<arch-dir>\<version>\<file>`. `check_printer_driver_files` applies that check to all files in `d->info8` and compares the result against `expect_exist`.

`remove_printer_driver_file` unlinks an uploaded source file from the driver share. `remove_printer_driver` removes each uploaded file, avoiding duplicate unlinks for config/dependent files that alias another file name.

## Driver Test Cases

`test_add_driver_arg` is the main test runner for one driver context. It fills remote server info, skips if local CUPS driver files are missing, uploads files, tests add/delete at levels 1, 2, 3, 4, 6, and 8 using bare file names, rewrites paths to full UNC driver-directory paths, repeats the level matrix, removes uploaded files, and returns the accumulated result. It skips levels 2 and 4 for Samba targets and level 8 for Windows Server 2003 targets.

`test_add_driver_ex_64`, `test_add_driver_ex_32`, `test_add_driver_64`, and `test_add_driver_32` create x64 and NT x86 driver contexts using `/usr/share/cups/drivers/x64` or `/usr/share/cups/drivers/i386`, driver files `pscript5.dll`, `cups6.ppd`, and `cupsui6.dll`, and select normal or Ex API behavior with different driver names.

`test_add_driver_adobe` and `test_add_driver_adobe_cupsaddsmb` are Samba3-only Windows 4.0 driver tests using Adobe-style driver files. The cupsaddsmb variant includes help, monitor, datatype, and a dependent file array.

`test_add_driver_timestamps` tests Ex driver date persistence twice: first with the current time converted to NT time and then with a one-second Unix timestamp converted to NT time.

`test_multiple_drivers` uploads one shared set of local files, registers three drivers with distinct names, deletes them one at a time, and asserts deleting one driver does not remove the others from enumeration.

`test_driver_copy_from_directory` builds a unique remote upload subdirectory from a GUID, sets `APD_COPY_NEW_FILES | APD_COPY_FROM_DIRECTORY | APD_RETURN_BLOCKING_STATUS_CODE`, adds a driver using full remote paths, deletes with `DPD_DELETE_ALL_FILES`, and verifies the versioned copied files no longer exist. x64 and x86 wrappers provide architecture-specific cases.

`test_del_driver_all_files` adds an Ex x64 driver with dependent files, deletes with `DPD_DELETE_ALL_FILES`, and verifies all copied driver files are gone.

`test_del_driver_unused_files` adds two x64 Ex drivers with overlapping files. It expects `DPD_DELETE_ALL_FILES` on the first driver to fail with `WERR_PRINTER_DRIVER_IN_USE`, then expects `DPD_DELETE_UNUSED_FILES` to delete only non-overlapping files. It confirms the second driver's files remain, deletes the second driver with `DPD_DELETE_ALL_FILES`, and confirms its files are gone.

`torture_rpc_spoolss_driver` registers the driver suite as an RPC interface tcase for `ndr_table_spoolss`, adding all normal, Ex, Adobe, timestamp, multiple-driver, copy-from-directory, and delete-file-semantics tests.

## State and Persistence Behavior

The tests intentionally create persistent server-side state: printers, print jobs, printer data values, published-printer attributes, driver registry entries, driver files in print$-style shares, and versioned driver files copied by the spooler. State is cleaned in fixture teardowns and per-driver test cleanup, but failures can leave server artifacts. The code mitigates this by using fixed torture names for predictable cleanup, GUID-named temporary upload directories for copy-from-directory tests, delete-after-add checks, purge-before-job-enum checks, and duplicate-file guards during manual source-file unlinking.

Printer handles and server handles are explicit `policy_handle` values that must be closed or invalidated by delete/close helpers. Driver file upload state is not tracked in an external manifest; it is reconstructed from `torture_driver_context` fields during removal and verification. Memory ownership is mainly `talloc`-scoped to `tctx` or per-driver contexts.

## Dependencies and Integration Points

This chunk integrates the Samba torture framework, DCE/RPC generated spoolss and winreg clients, NDR decoding, SMB client libraries, loadparm client options, command-line credentials, event contexts, and target-specific torture settings such as `samba3`, `samba4`, `w2k3`, and `host`.

It assumes a target server with spoolss enabled, available static printer share `print1` for the SMB2 spooling test, accessible print driver share derived from `GetPrinterDriverDirectory`, and local driver fixture files under `/usr/share/cups/drivers/...` for driver upload tests. Some tests are deliberately skipped for Samba or older Windows targets where the expected behavior differs or support is incomplete.

## Risks and Edge Cases

- The SMB2 spooling test documents a race between dynamically added printers and separate spoolss worker processes, so it hard-codes `TORTURE_PRINTER_STATIC1`.
- Many driver tests depend on local CUPS driver files. Missing files cause skips, reducing coverage silently unless the test environment tracks skips.
- Fixed driver names such as `torture_driver_add`, `torture_driver_ex`, and `torture_driver_deleter` can collide with leftovers from failed prior runs.
- Cleanup is best effort in some paths. Driver file removal warnings during fixture teardown may leave remote files or registry entries.
- `upload_printer_driver_file` logs read/write warnings and breaks its loop, but still proceeds to close and return success unless later assertions fail, so partial file uploads may produce add-driver failures farther downstream.
- Path-prefix assertions check that returned paths start with the driver directory, but they do not canonicalize case, separators, or equivalent UNC forms.
- Delete-file tests are sensitive to server-side reference counting for shared files. Incorrect overlap modeling or stale server state can change expected `WERR_PRINTER_DRIVER_IN_USE` and file-existence outcomes.
- Publish/unpublish checks allow pending states, reflecting asynchronous directory publishing behavior.

## Test Signals

Strong success signals are returned `WERROR` values, transport `NTSTATUS`, enumeration counts, exact job counts, post-delete enumeration misses, registry verification through a separate `winreg` pipe, driver path-prefix checks, driver timestamp/version equality, BIDI and GDI buffer-size responses, OS version equality between `GetPrinter` level 0 and `OSVersion` printer data, and SMB file existence checks after delete flags.

The main failure signals are `torture_assert*` failures, `torture_fail` for leaked deleted drivers or remote-file open failures, and skips for unsupported Samba/Windows target combinations or missing local driver directories. The chunk's suite registration exposes these signals through the Samba torture runner under `spoolss`, `spoolss.printer`, and `spoolss.driver`.
