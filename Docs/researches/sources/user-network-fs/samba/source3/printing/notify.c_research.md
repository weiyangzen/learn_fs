# sources/user-network-fs/samba/source3/printing/notify.c

## Purpose
`notify.c` batches and sends spoolss printer/job change notifications to interested Samba processes. It queues `spoolss_notify_msg` records, coalesces noisy job progress updates, serializes messages, finds subscribed PIDs from per-printer print databases, and sends low-priority messaging events.

## Important APIs, types, and functions
- `print_queue_snum(qname)` maps a printable share name to a loadparm service number.
- `print_notify_send_messages(msg_ctx, timeout)` flushes the pending global queue by printer.
- `notify_printer_status*`, `notify_job_status*`, `notify_job_total_bytes`, `notify_job_total_pages`, `notify_job_username`, `notify_job_name`, `notify_job_submitted`, and printer metadata helpers enqueue typed field notifications.
- `send_spoolss_notify2_msg` appends to the pending queue and schedules a one-second tevent timer.
- `flatten_message` serializes a queued message with tdb packing.
- `print_notify_pid_list` reads subscribed PIDs from the printer TDB under `NOTIFY_PID_LIST_KEY`.

## Control flow
Public notification helpers first respect `lp_disable_spoolss`, create the global send talloc context, allocate/fill a `spoolss_notify_msg`, and pass it to `send_spoolss_notify2_msg`. That function replaces existing queued `TOTAL_BYTES`/`TOTAL_PAGES` messages for the same printer/job/field when the queue is still below 100 messages, reducing client flicker, otherwise appends a deep-copied message to `notify_queue_head`. If an event context is supplied, it schedules a one-second timer. The timer switches to root and calls `print_notify_send_messages`, which repeatedly groups messages by printer, serializes a count-prefixed buffer, removes sent messages from the queue, reads interested PIDs, and sends `MSG_PRINTER_NOTIFY2 | MSG_FLAG_LOWPRIORITY` to each PID until an optional timeout expires.

## State and persistence behavior
Runtime state is held in global `send_ctx`, `num_messages`, `notify_queue_head`, and `notify_event`. The subscription list is persisted outside this file in per-printer print TDB records. After a flush, child allocations under `send_ctx` are freed and `num_messages` resets to zero.

## Dependencies and integration points
The file depends on source3 printing structures, generated spoolss constants, messaging, tevent, loadparm, tdb packing/unpacking helpers, and print database helpers such as `get_print_db_byname` and `get_printer_notify_pid_list`. It is called by print queue/job update paths and feeds clients waiting on spoolss change notifications.

## Risks and edge cases
- Global queue state is process-local and not protected by explicit locks; it assumes normal smbd event-loop serialization.
- If allocation fails during flattening or batching, queued children can be freed and notifications dropped.
- `print_notify_pid_list` assumes PID records are 8-byte entries and reads only the low 32-bit value with `IVAL`, which is sensitive to platform PID size/record format.
- Message send results are not checked, so dead subscribers are tolerated but not pruned here.
- A zero or missing event context means queued messages require an explicit flush call.

## Test signals
Tests should enqueue value and buffer notifications, verify coalescing for job byte/page updates, serialize multiple messages for one printer, simulate PID-list records in a print TDB, and confirm `lp_disable_spoolss` suppresses enqueueing. Event-loop tests can assert the one-second timer flushes and clears queue state.
