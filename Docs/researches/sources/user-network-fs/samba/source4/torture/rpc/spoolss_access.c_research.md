# sources/user-network-fs/samba/source4/torture/rpc/spoolss_access.c

## Purpose

`spoolss_access.c` is a Samba torture suite for print spooler access-control behavior. It creates several temporary domain users, gives selected users built-in group memberships, privileges, or explicit printer security descriptor ACEs, then verifies which `spoolss_OpenPrinterEx` access masks succeed against print-server and printer handles.

## Important APIs, Types, and Functions

The local state types are `struct torture_user`, which describes the test identity and expected rights, and `struct torture_access_context`, which carries the spoolss pipe, selected printer name, original printer security descriptor, and created user handle. `test_openprinter_handle()` and `test_openprinter_access()` wrap `spoolss_OpenPrinterEx` and optional `ClosePrinter`. Setup helpers include `spoolss_access_setup_membership()` for SAMR BUILTIN alias membership, `spoolss_access_setup_privs()` for LSA account rights, `spoolss_access_setup_sd()` for printer DACL mutation, and `test_EnumPrinters_findone()` for selecting a printer. The exported suite factory is `torture_rpc_spoolss_access()`.

## Control Flow

Each fixture allocates a `torture_access_context`, fills the user profile, and calls `torture_rpc_spoolss_access_setup_common()`. The common setup creates a SAMR test user, builds credentials, optionally adds group membership or LSA rights, connects to spoolss as an administrator to find a printer, optionally adds printer ACEs, then reconnects to spoolss as the new user. `test_openprinter()` iterates a fixed table of server and printer access masks and compares results with expectations derived from `admin_rights` and `system_security`. Teardown deletes the test user and restores the original printer security descriptor for the security-descriptor fixture.

## State and Persistence Behavior

The suite mutates the test domain by creating accounts named `torture_user*`, changing BUILTIN alias memberships, and adding account rights. The `normaluser_sd` fixture also mutates a real printer DACL and preserves `sd_orig` for restoration. Membership and privilege cleanup are explicitly left as comments, so user deletion is the main cleanup mechanism for those changes. If teardown is interrupted after DACL mutation, printer permissions may remain changed until restored manually.

## Dependencies and Integration Points

The file depends on generated spoolss, SAMR, LSA, and security NDR client stubs; `torture_rpc_connection()`, test user helpers from `testjoin.c`, spoolss helper routines such as `test_GetPrinter_level()` and `test_ClosePrinter()`, Samba credentials/loadparm state, and domain policy supporting SAMR account creation.

## Risks and Edge Cases

Tests depend on at least one enumerable local printer and on server support for the relevant privileges. The XPS printer is skipped only when multiple printers exist, so printer selection can affect results. The privilege setup path treats missing privileges as a skip signal rather than a hard failure. Teardown restores printer security only when `printername` is present, and handle close coverage is best effort. The expected access matrix encodes Windows/Samba behavior and is sensitive to ACL inheritance, administrator mapping, and print operator privilege semantics.

## Test Signals

Strong signals are successful `normaluser`, `adminuser`, `printopuser`, `printopuserpriv`, `normaluser_sd`, and machine-workstation `openprinter` cases. Failures isolate to SAMR user creation, LSA right assignment, printer enumeration, printer DACL restore, or individual `OpenPrinterEx` access-mask expectations.
