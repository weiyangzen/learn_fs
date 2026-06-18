## sources/security-integrity/audit-userspace/src/ausearch-options.h

Purpose: exports `ausearch` option-derived globals and the command-line parsing entry point.

Important APIs/types: declares `event_key`, `event_subject`, `event_object`, `event_se`, `just_one`, `line_buffered`, `event_debug`, `event_ppid`, `event_session_id`, `event_type`, `report_format`, and `check_params()`.

Control flow/state: after `check_params()` succeeds, consumers read these globals directly rather than receiving a criteria object.

Dependencies/integration: includes `ausearch-common.h` and `ausearch-int.h`, linking option state to shared search enums and integer lists.

Risks/test signals: this header only exposes a subset of globals defined in the `.c`; other modules use additional `extern` declarations. Tests should guard against missing cleanup and conflicting duplicate declarations when adding options.
