# sources/user-network-fs/samba/source4/torture/rpc/iremotewinspool_driver.c

## Purpose
This file defines the `rpc.iremotewinspool_driver` suite for uploading, installing, validating, and cleaning up printer driver packages through iremotewinspool. It combines local INF parsing, SMB copy to `print$`, Winspool package RPCs, and Winreg validation.

## Important APIs, Types, And Functions
`torture_rpc_iremotewinspool_drv()` registers a fixture-backed `drivers` tcase. Setup helpers collect required torture options (`driver_path`, `inf_file`, `driver_name`, `driver_arch`, optional `core_driver_inf`), parse the INF into `spoolss_AddDriverInfo8`, open iremotewinspool, discover environment, create a random upload GUID directory, and connect to `print$` over SMB1. `test_CopyDriverFiles()` walks the local driver tree with `tftw()` and copies files through SMB. `test_UploadPrinterDriverPackage()`, `test_InstallPrinterDriverFromPackage()`, and `test_ValidatePrinterDriverInstalled()` drive the main workflow. Teardown deletes the upload directory, exits the SMB session, uninstalls the driver, removes the package, and closes the printer handle.

## Control Flow
The intended sequence is: fixture setup, copy local package into `\\server\print$\{GUID}`, call `AsyncUploadPrinterDriverPackage` with `UPDP_UPLOAD_ALWAYS`, store the returned destination INF path, call `AsyncInstallPrinterDriverFromPackage` with parsed driver name/environment and `IPDFP_COPY_ALL_FILES`, then connect to Winreg over `ncacn_np` and verify the installed driver key has an `InfPath` matching the upload result.

## State And Persistence Behavior
This suite is highly stateful. It creates directories and files on the remote `print$` share, uploads a driver package into the driver store, installs a printer driver, writes/observes registry entries under `SYSTEM\CurrentControlSet\Control\Print`, and removes those artifacts in teardown. Cleanup is best-effort: teardown calls uninstall and package removal regardless of test failures, but partially initialized fields or failed uploads can make cleanup incomplete.

## Dependencies And Integration Points
Dependencies include generated Winspool, Spoolss, and Winreg stubs; SMB client APIs; raw SMB session exit; registry conversion helpers; local filesystem walking; printer-driver INF parsing; command-line credentials; loadparm resolver/socket/gensec settings; and common iremotewinspool helpers.

## Risks And Edge Cases
Running this against a real print server can install or remove printer drivers. SMB1 is required on Windows for the `print$` connection path. The architecture option validation appears inverted: it sets `valid = true` when `strequal(*p, driver_arch) == 0`, which looks like it may accept non-matching entries rather than the matching one depending on Samba `strequal()` semantics. Teardown assumes `dinfo`, SMB connection, upload directory, and uploaded INF path are valid, so setup failures can produce cleanup hazards.

## Test Signals
Signals include successful option collection, INF class containing `PRINTER_DRIVER_CLASS`, successful SMB tree copy, HRESULT success for upload/install/remove package, WERR success for uninstall, successful Winreg key open, and case-insensitive equality between registry `InfPath` and the uploaded INF path.
