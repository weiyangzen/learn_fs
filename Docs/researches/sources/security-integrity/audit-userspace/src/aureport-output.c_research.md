# sources/security-integrity/audit-userspace/src/aureport-output.c

## Purpose
`aureport-output.c` prints report titles, per-event detailed rows, and summary wrap-up tables for `aureport` based on scanner results and option globals.

## Important APIs, Types, And Functions
Public functions are `print_title`, `print_per_event_item`, and `print_wrap_up`. Internal functions include `print_title_summary`, `print_title_detailed`, `do_summary_output`, and summary printers for file/string/user/int/syscall/type lists.

## Control Flow
`print_title` resets line numbering and selects summary or detailed title output. `print_per_event_item` formats one `llist` event according to `report_type`, using lookup helpers for syscall, uid, success, message type, TTY data, AVC lists, and safe string printing. `print_wrap_up` runs only for summary mode, sorts the relevant aggregate list in `sd`, then prints the appropriate summary. `do_summary_output` prints global ranges and aggregate counters.

## State And Persistence
Local state is only `line_item`. It consumes global `report_type`, `report_detail`, `report_format`, filter flags, scanner summary `sd`, `start_time/end_time`, and first/last event globals. It writes to stdout and does not persist files.

## Dependencies And Integration
It depends on `aureport-scan.h`, `aureport-options.h`, and `ausearch-lookup.h`. The scanner calls `print_per_event_item` while walking events and `print_wrap_up` after aggregation.

## Risks
Output paths assume many fields are non-null for specific reports; some branches guard with `?`, others pass values directly. `RPT_AVC` can emit multiple rows per event. `RPT_TTY` mutates the message buffer by replacing a trailing space with NUL before printing. Summary output depends on scanner-maintained aggregate lists and event range globals being initialized.

## Test Signals
No output-specific unit tests are present. Golden-output tests should cover each report type in detailed and summary modes, interpreted/default type formatting, empty aggregates, safe printing of spaces/control characters, AVC multi-row output, TTY data decoding, and null field handling.
