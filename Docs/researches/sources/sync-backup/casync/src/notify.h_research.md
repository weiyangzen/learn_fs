# sources/sync-backup/casync/src/notify.h

Purpose: tiny public header for readiness notification.

Important APIs/types/functions: declares `send_notify(const char *text)`. The include guard name is idiosyncratic but effective.

Control flow/state: none in the header; callers pass complete notification payloads such as `READY=1`.

Dependencies/integration: paired with `notify.c`; included by components that need to synchronize background helper startup with shell tests.

Risks/test signals: since only the declaration is here, ABI mismatch risk is low. Correctness depends on callers using newline-compatible sd_notify payload syntax and handling `0` when no notification socket exists.

Source research group: `subset-b-009122`.
