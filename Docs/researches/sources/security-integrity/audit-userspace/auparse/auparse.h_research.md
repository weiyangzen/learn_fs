# sources/security-integrity/audit-userspace/auparse/auparse.h

Purpose: Installed public header for libauparse consumers.

Important APIs, types, and functions: Declares opaque `auparse_state_t`, callback/destroy callback types, lifecycle (`auparse_init()`, `auparse_destroy()`, `auparse_destroy_ext()`), buffer/feed APIs, callback registration, escape mode and metrics, search API, normalization API, event traversal, record traversal, field traversal, raw and interpreted accessors, and socket/realpath interpretation helpers. Uses attribute compatibility macros for allocation/deallocation and access annotations.

Control flow: The header describes library usage flow: initialize with an `ausource_t`, optionally add callbacks or search rules, iterate events/records/fields or feed data, then destroy. Callback users receive `AUPARSE_CB_EVENT_READY`.

State and persistence: Parser state is opaque. Accessor return ownership varies: e.g. `auparse_get_node()` is annotated for free/deallocation, while most strings are borrowed from parser state.

Dependencies and integration points: Includes `auparse-defs.h` and provides C++ linkage guards. This is the API consumed by applications, audisp plugins, and tests.

Risks and edge cases: ABI stability matters for every declaration. Callers must respect cursor semantics; many accessors depend on a current event, current record, and current field. Misunderstanding returned string ownership can cause leaks or invalid frees.

Test signals: Public compilation tests, ABI checks, and behavioral tests using the API are the key signals. The z/OS remote plugin in this subset is a concrete consumer of feed, callback, event timestamp, record, field, and interpretation APIs.
