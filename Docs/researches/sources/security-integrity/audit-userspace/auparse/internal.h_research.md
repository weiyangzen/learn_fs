<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/internal.h -->
# sources/security-integrity/audit-userspace/auparse/internal.h

## Purpose
Defines auparse private state, event accumulation structures, normalization state containers, and hidden internal helper prototypes shared across the auparse implementation.

## Important APIs, types, and functions
Important types include `auparser_state_t`, `au_lol_t`, `au_lolnode`, `au_lol`, `nv_pair`, `value_t`, `subject`, `object`, `normalize_data`, and `struct opaque`. Hidden functions include config loading/freeing, `lookup_uid_from_name`, `init_normalizer`, and `clear_normalizer`.

## Control flow
This header has no executable flow, but it models the parser lifecycle: source input feeds `opaque.databuf`, records accumulate in `event_list_t` or list-of-lists state, search expressions and cursor fields guide matching, callbacks report parser events, and normalization/interpretation caches hang off the parser state.

## State and persistence behavior
`struct opaque` holds nearly all parser runtime state: input source descriptors, buffers, current event list, search expression, callbacks, list-of-lists event cache, escape/message modes, normalization data, per-parser interpretation list, and UID/GID LRUs. State is in-memory and per parser.

## Dependencies and integration points
Pulls in auparse definitions, event-list and data-buffer types, auditd config, normalize list support, DSO visibility, nvlist, lru, and standard I/O. It is the central integration point for parsing, searching, interpreting, normalization, callbacks, and config.

## Risks and test signals
Risks are lifetime coupling across buffers, event-list nodes, cached interpretation strings, and callback user data. List-of-lists handling must tolerate interleaved events and timeout completion. Tests should stress multi-record interleaving, callback cleanup, cache destruction, normalization reset, and source switching.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/internal.h -->
