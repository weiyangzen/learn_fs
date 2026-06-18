# sources/user-network-fs/samba/source3/printing/notify.h

## Purpose
`notify.h` declares the source3 printing notification API implemented by `notify.c`.

## Important APIs, types, and functions
- `print_queue_snum` resolves printable queue names to service numbers.
- `print_notify_send_messages` flushes pending queued notifications.
- Printer notification helpers cover status, driver, comment, share name, printer name, port, location, separator file, and generic by-name field updates.
- Job notification helpers cover status, total bytes, total pages, username, document name, and submitted time.

## Control flow
The header is declarative. Callers include it to enqueue spoolss notifications while supplying a `tevent_context`, `messaging_context`, printer/share identifier, job id, and field-specific value.

## State and persistence behavior
No state lives in the header. The declared functions mutate process-local notification queue state and interact with printer TDB subscriber state in `notify.c`.

## Dependencies and integration points
The API exposes notification functions to printing, spoolss, and queue-processing code. Including code needs declarations for `struct tevent_context`, `struct messaging_context`, `time_t`, and fixed-width integer types from Samba common headers.

## Risks and edge cases
The API mixes service-number and printer-name entry points. Callers must choose the correct helper and pass valid share names/job ids so clients receive notifications on the expected printer.

## Test signals
Compile coverage catches signature drift. Behavioral tests belong with `notify.c` and should exercise every declared helper at least enough to verify field type, id, and payload length.
