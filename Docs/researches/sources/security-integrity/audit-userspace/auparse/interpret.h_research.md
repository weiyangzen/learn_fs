<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/interpret.h -->
# sources/security-integrity/audit-userspace/auparse/interpret.h

## Purpose
Declares hidden auparse interpretation APIs shared between field parsing, nvlist handling, ausearch lookup code, and cache lifecycle code.

## Important APIs, types, and functions
Defines `NEVER_LOADED` sentinel and prototypes for interpretation-list lifecycle, type lookup, `do_interpret`, UID/GID cache destruction/metrics, and `au_unescape`.

## Control flow
Consumers initialize the interpretation list when parser state is created, optionally load auditd-provided interpreted text, call `do_interpret` lazily for current fields, and free caches/lists during parser teardown.

## State and persistence behavior
The sentinel distinguishes never-loaded interpretation lists from empty loaded lists. The header exposes no persistence; all state lives in `auparse_state_t`.

## Dependencies and integration points
Depends on `config.h`, DSO visibility, `rnode.h`, time definitions, and GCC attributes. It integrates `interpret.c` with `nvlist.c`, parser teardown, and external ausearch support.

## Risks and test signals
Risks are mismatched ownership expectations for malloc-returning functions and misuse of `NEVER_LOADED`. Tests should check list counts before/after load/free and that interpreted field values are cached and released correctly.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/interpret.h -->
