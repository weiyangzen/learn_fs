# File Research: sources/windows/winfsp/src/dll/eventlog/eventlog.h

Generated-style Event Log message identifier header.

Key contents:
- Documents the standard 32-bit Windows message ID layout: severity, customer bit, reserved bit, facility, and code.
- Defines three WinFsp event IDs:
  - `FSP_EVENTLOG_INFORMATION` as `0x60000001L`
  - `FSP_EVENTLOG_WARNING` as `0xA0000001L`
  - `FSP_EVENTLOG_ERROR` as `0xE0000001L`
- All messages have the text shape `%1: %2`.

Dependencies:
- Consumed by `eventlog.c` when selecting event IDs for `ReportEventW`.

Filesystem relevance:
- Provides diagnostic message constants for service/DLL event reporting; no runtime filesystem logic is implemented here.

Notable risks:
- Must remain synchronized with the corresponding message resource compiled into the DLL/sys event message file.
