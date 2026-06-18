# sources/user-network-fs/samba/source3/rpc_client/init_spoolss.h

## Purpose
`init_spoolss.h` declares the spoolss initialization, conversion, and default object helpers used by print RPC client/server support code.

## Important APIs, Types, And Functions
The header exposes time conversion, driver version parsing, printer-data NDR union push/pull, `PrinterInfo2` to `SetPrinterInfo2` mapping, add-driver-info normalization, default devmode/security descriptor creation, architecture name shortening, and `spoolss_UserLevel1` initialization.

## Control Flow
There is no runtime logic. It defines a compact API surface for helpers that are implemented in `init_spoolss.c` and consumed by winreg-backed printer persistence and spoolss server routines.

## State And Persistence
The header itself stores nothing. Its declared constructors return talloc-owned structures that callers may persist through registry or RPC state.

## Dependencies And Integration Points
Consumers need generated spoolss and winreg types. Primary integration is `cli_winreg_spoolss.c`, spoolss server implementation, printing migration, and printer administration tools.

## Risks
Because the header is a shared print subsystem contract, signature changes can break several server and client paths. Callers need to respect talloc ownership and the shallow-copy behavior of conversion helpers.

## Test Signals
Compile coverage plus spoolss printer create/update, driver upload, default security descriptor, and NDR printer data tests are the strongest signals.
