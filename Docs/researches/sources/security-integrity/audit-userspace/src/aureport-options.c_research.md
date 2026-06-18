# sources/security-integrity/audit-userspace/src/aureport-options.c

## Purpose
`aureport-options.c` parses `aureport` command-line options and initializes global report and search-selector state used by the scanner and output layers.

## Important APIs, Types, And Functions
Public API is `check_params`. Global outputs include `user_file`, `force_logs`, `no_config`, parser-compatible `event_*` filters, `arg_eoe_timeout`, `report_type`, `report_detail`, `report_format`, `event_failed`, `event_conf_act`, `event_success`, and `escape_mode`. Internals include `optiontab`, `audit_lookup_option`, `usage`, `set_report`, and `set_detail`.

## Control Flow
`check_params` walks argv manually, infers optional arguments by checking whether the next token begins with `-`, maps option strings to enum values, enforces one report type, sets detailed/summary modes, primes scanner filters with dummy sentinels, parses time windows through `ausearch_time_start/end`, appends node filters, parses escape mode and EOE timeout, handles help/version exits, and defaults to summary report if no report was selected.

## State And Persistence
The file is almost entirely global mutable state. It does not persist to disk, but it determines which audit records are scanned and how output is interpreted. Some allocated state, such as `user_file` and node strings, is handed to later program lifetime cleanup.

## Dependencies And Integration
It depends on `aureport-options.h`, `ausearch-time.h`, `libaudit.h`, `auparse-defs.h`, passwd/group/time headers, and scanner-compatible globals declared elsewhere. `aureport.c` calls `check_params`, and `aureport-output.c` consumes `report_type`, `report_detail`, `report_format`, and filters.

## Risks
Manual option parsing can misclassify negative values as options. Many report filters are set by sentinel values like `dummy`, which requires scanner code to interpret presence rather than actual value. Several specific report options are still `UNIMPLEMENTED` and exit immediately. Global state makes repeated invocations in one process unsafe unless reinitialized.

## Test Signals
No focused option tests are present. Tests should exercise every report selector, conflicting report types, default summary mode, time parsing permutations, node list allocation, escape mode parsing, EOE timeout validation, and unsupported option error paths.
