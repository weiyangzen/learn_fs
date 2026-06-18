# sources/user-network-fs/samba/source4/torture/ndr/spoolss.c

## Purpose

`spoolss.c` is a large NDR torture fixture for Samba's print-spooler RPC IDL. It decodes captured `spoolss` and `winspool_Async*` request/response blobs for printer open/close/query/data/driver/key/form/notification/job/property operations, including classic NDR and NDR64 paths.

## Important APIs, Types, and Functions

- Includes `librpc/gen_ndr/ndr_spoolss.h` through the generated torture interfaces, plus generic torture helpers and printing/security-related generated types.
- Static fixtures cover `OpenPrinterEx`, `ClosePrinter`, `GetPrinter`, `GetPrinterData`, `ReplyOpenPrinter`, `ReplyClosePrinter`, `RemoteFindFirstPrinterChangeNotifyEx`, `RouterRefreshPrinterChangeNotify`, `EnumForms`, `EnumPrinterDataEx`, `EnumPrinterKey`, `FindClosePrinterNotify`, `GetPrinterDriverDirectory`, `AddPrinterDriverEx`, `GetPrinterDriver2`, `SetPrinter`, `GetCorePrinterDrivers`, and `SetJobNamedProperty`.
- Async equivalents are registered for many operations: `winspool_AsyncOpenPrinter`, `AsyncClosePrinter`, `AsyncGetPrinter`, `AsyncGetPrinterData`, `AsyncEnumForms`, `AsyncEnumPrinterDataEx`, `AsyncEnumPrinterKey`, `AsyncGetPrinterDriverDirectory`, `AsyncAddPrinterDriver`, `AsyncGetPrinterDriver`, `AsyncSetPrinter`, `AsyncGetCorePrinterDrivers`, and `AsyncSetJobNamedProperty`.
- `getprinterdriver2_in_check()` asserts architecture, info level, offered buffer size, and client version values.
- `getprinterdriver2_out_check()` deeply validates a level-6 Ricoh x64 driver response, paths, dependent files, version fields, manufacturer/provider metadata, needed size, server version outputs, and `WERR_OK`.
- `setjobnamedproperty_req_check()` validates job id and `SPLFILE_CONTENT_TYPE_*` named-property decoding.
- `setprinter_level_3_xpsp3_req_check()` validates a policy handle GUID, level-3 info, empty devmode, and security descriptor container details.
- `ndr_spoolss_suite()` registers dozens of pull and pull-IO tests, including `LIBNDR_FLAG_NDR64` variants.

## Control Flow

The suite constructor is a long linear registration table. For each captured operation, it registers request, response, or paired request/response blobs with the generated NDR pull framework. Many operations are registered twice: once for synchronous `spoolss_*` and once for equivalent async `winspool_Async*` forms. The NDR64 cases use `torture_suite_add_ndr_pull_fn_test_flags()` to force `LIBNDR_FLAG_NDR64`.

Most tests rely on successful decode as the assertion. A smaller set invokes explicit callbacks for high-value structures: `GetPrinterDriver2`, `SetJobNamedProperty`, and an XP SP3-style `SetPrinter` level-3 security descriptor. Combined IO tests validate direction-sensitive request/response parsing for buffer-size negotiation and result handling.

## State and Persistence Behavior

The file has no live spooler state. Handles, printer names, driver paths, form data, registry-key names, security descriptors, and job properties are static captured wire representations. No printer configuration is changed and no files are read from print shares. Decoded state lives only for the duration of each torture test.

## Dependencies and Integration Points

This is an integration point between Samba's generated spoolss/winspool NDR parsers and the torture test harness. It also indirectly depends on generated constants for driver versions, property names, RPC property value types, security descriptor fields, WERROR helpers, GUID parsing, and NDR64 support. Because the same blobs are registered against sync and async RPC shapes, it helps detect divergence between related IDL definitions.

## Risks and Edge Cases

- The file is fixture-heavy; many registered tests have `NULL` callbacks and only prove that parsing completes.
- Some complex data, such as printer data blobs, driver private data, and security ACL contents, is only partially validated.
- Hard-coded server/printer names, UNC paths, driver versions, and GUIDs encode historical Windows behavior. Intentional IDL normalization can cause noisy fixture failures.
- NDR64 coverage is valuable but narrow: it covers selected open, set, and core-driver requests, not every response or error variant.
- The large source size and many byte arrays make maintenance error-prone; adding or editing fixtures without semantic callbacks can reduce regression value.

## Test Signals

Strongest signals are the explicit checks for `GetPrinterDriver2` level 6, named job property decoding, XP SP3 `SetPrinter` security descriptor parsing, paired IO tests for buffer negotiation, and dual sync/async registrations. Weaker signals are decode-only fixtures. The relevant validation surface is the Samba NDR torture suite filtered to `spoolss`.
