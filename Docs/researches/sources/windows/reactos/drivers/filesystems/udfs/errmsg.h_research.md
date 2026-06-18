# File Research: sources/windows/reactos/drivers/filesystems/udfs/errmsg.h

## Purpose

`errmsg.h` defines event-log message constants for the UDFS driver. It is generated or kept in message-compiler style from an `errmsg.msg` source, with comments documenting NTSTATUS bit layout and severity values.

## Contents

The file defines severity constants:

- `STATUS_SEVERITY_WARNING`
- `STATUS_SEVERITY_SUCCESS`
- `STATUS_SEVERITY_INFORMATIONAL`
- `STATUS_SEVERITY_ERROR`

It defines one UDFS event id:

- `UDF_ERROR_INTERNAL_ERROR ((ULONG)0xE004A001L)`: message text indicates the UDF FSD encountered an internal error and log data should be checked.

## Integration Points

Dispatch wrappers such as `UDFCreate`, `UDFDeviceControl`, and `UDFDirControl` call `UDFLogEvent(UDF_ERROR_INTERNAL_ERROR, RC)` from exception handlers. This constant is the common event-code hook used when unexpected kernel exceptions are caught.

## Notable Risks

The comments instruct message IDs to begin at `0xA000` for UDFS errors and avoid `%1` insertion strings. Only one message constant is present, so any more specific event reporting must be defined elsewhere or added to this message set.
