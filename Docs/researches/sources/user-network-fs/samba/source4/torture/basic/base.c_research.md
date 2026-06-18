# sources/user-network-fs/samba/source4/torture/basic/base.c

## Purpose
This large file registers and implements many foundational SMB1 torture tests. It covers connection setup, TID/VUID isolation, attributes and TRANS2 metadata, negotiation behavior, tree-connect device types, read/write integrity, deferred opens, open/share/delete semantics, xcopy/iometer patterns, path checking, Samba3 error mappings, birth time stability, timewarp root opens, and GMT search masks.

## Important APIs, Types, And Functions
The exported initializer is `torture_base_init`. Major local tests include `open_nbt_connection`, `run_fdpasstest`, `run_attrtest`, `run_trans2test`, `run_negprot_nowait`, `run_tcon_test`, `run_tcon_devtype_test`, `rw_torture2`, `run_readwritetest`, `run_deferopen`, `run_vuidtest`, `run_opentest`, `run_xcopy`, `run_iometer`, `torture_chkpath_test`, `torture_samba3_errorpaths`, `run_birthtimetest`, `torture_smb1_twrp_openroot`, and `torture_smb1_find_gmt_mask`. It also registers many tests implemented in sibling files.

## Control Flow
Most tests open one or two SMB connections, create temporary files/directories, perform protocol operations, assert status codes and side effects, then clean up. `run_opentest` is the densest path, checking invalid control characters, readonly error selection, truncate behavior on readonly opens, temporary file creation, non-IO opens with delete access, sharing behavior, and lock/truncate interactions. `torture_base_init` creates the `"base"` suite and registers one-SMB, two-SMB, multi-SMB, nested-suite, benchmark, scan, and simple tests.

## State And Persistence
The file deliberately mutates target SMB shares by creating, opening, writing, locking, listing, setting attributes, and deleting temporary paths. It temporarily changes client loadparm settings in the Samba3 error-path test and restores them. Repository state is not changed.

## Dependencies And Integration Points
It depends on `libcli`, raw SMB APIs, torture utility helpers, loadparm, events, resolver support, filesystem/time wrappers, and many sibling torture suites. It is a central integration point for SMB1 server/client behavior and is used to detect regressions in both Samba and third-party SMB servers.

## Risks And Test Signals
Risks include timing-sensitive sleeps, environment changes such as `TZ=GMT`, benchmark tests depending on `torture_numops`, cleanup after early failures, broad server-specific assumptions, and skipped timewarp tests without settings. Test signals include exact NTSTATUS/DOS mappings, data integrity across connections, no cross-VC handle leakage, correct TID/VUID rejection, create/open/share-mode compatibility, metadata timestamp behavior, and suite registration coverage.
