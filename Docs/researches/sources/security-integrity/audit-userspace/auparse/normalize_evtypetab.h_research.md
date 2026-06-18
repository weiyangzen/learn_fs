<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/normalize_evtypetab.h -->
# sources/security-integrity/audit-userspace/auparse/normalize_evtypetab.h

## Purpose
Maps internal normalized event-kind constants to public string labels.

## Important APIs, types, and functions
The `_S` table maps `NORM_EVTYPE_*` values to strings such as `user-space`, `configuration`, `audit-daemon`, `mac-decision`, `audit-rule`, `dac-decision`, and `bpf-program`.

## Control flow
Generated `evtype_i2s` is called by `normalize_determine_evkind` in `normalize.c`.

## State and persistence behavior
Static map data only.

## Dependencies and integration points
Depends on `normalize-internal.h`. Integrated with `auparse_normalize_get_event_kind`.

## Risks and test signals
Risks are unmapped event-type constants and user-visible label churn. Tests should validate representative audit record types return expected event-kind strings.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/normalize_evtypetab.h -->
