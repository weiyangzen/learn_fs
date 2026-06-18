## sources/security-integrity/audit-userspace/src/ausearch-time.h

Purpose: public interface for time keyword lookup and filter parsing.

Important APIs/types: enum constants for recognized relative time keywords and declarations for `lookup_time()`, `ausearch_time_start()`, and `ausearch_time_end()`.

Control flow/state: successful parse writes shared `start_time`/`end_time` globals declared through `ausearch-common.h`.

Dependencies/integration: includes `ausearch-common.h`; used by option parsing.

Risks/test signals: enum values are internal contract with `timetab`; adding keywords requires updating both header and implementation. Tests should assert unknown keyword returns `-1` and all declared keywords parse.
