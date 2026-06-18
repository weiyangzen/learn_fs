# File Research: sources/windows/dokany/sys/util/ntstatus_log.inc

## Purpose
Large generated-style switch-body include used by Dokany kernel logging to turn `NTSTATUS`-family values into readable symbolic names.

## Main Behavior
- Contains 2,692 `case <STATUS>: return "<STATUS>";` entries and no enclosing function, switch, or default case.
- Included directly inside `DokanGetNTSTATUSStr(NTSTATUS Status)` in `sources/windows/dokany/sys/util/log.c`.
- Maps standard success, informational, warning, error, debug, RPC, ACPI, filter manager, Side-by-Side, cluster, transaction, log, graphics, BitLocker/FVE, Windows Filtering Platform, NDIS, TPM, Hyper-V, volume manager, VHD, Storage Spaces, SMB, secure boot, and app execution status constants.
- Unknown statuses fall through to `DokanGetNTSTATUSStr`'s enclosing `"Unknown"` return in `log.c`.

## Integration Points
- Used by `DOKAN_LOG_END_MJ`, mount manager logging, create/oplock logging, notification logging, and other diagnostic paths that call `DokanGetNTSTATUSStr`.
- Registered in the Visual Studio project as a non-compiling include item.
- Depends on Windows kernel headers defining every referenced status macro for the selected WDK target.

## Risks and Notes
- The file is data for diagnostics only; it does not affect IRP completion status values.
- Because entries are raw `case` labels, undefined constants or duplicate constant values become compile-time failures in the including translation unit.
- Several returned strings are visibly truncated compared with their case names, for example some names ending in `FULL`, `FAIL`, `LEVEL`, or `DLL`. That can make logs imprecise but not semantically wrong for control flow.
- There are no conditional guards for version-specific status constants, so WDK version compatibility is tied to the status set captured in this file.
