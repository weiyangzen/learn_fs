# sources/security-integrity/selinux/libsemanage/include/semanage/boolean_record.h

Purpose: defines the public opaque record API for a policy boolean record. It separates key construction/comparison from mutable record fields so the same object model can be used by local files, policydb views, joins, and language bindings.

Important APIs/types/functions: declares the opaque record type `semanage_bool_t`, its key type, key create/extract/free helpers, `compare`/`compare2`, field getters and setters, and create/clone/free routines. The main identity is `semanage_bool_key_t` keyed by boolean name; booleans carry a name and enabled/disabled integer value.

Control flow: clients allocate a record with the create API, fill fields with setters, derive or create a key, then pass both to local modify/set/query APIs. Query and list APIs return records that follow the same free routine. Clone APIs deep-copy nested strings, arrays, and contexts where applicable.

State and persistence behavior: the header itself has no persistence, but setter ownership rules define what later database backends will persist. Setters take a `semanage_handle_t` for allocation, validation, message reporting, and libsepol interop.

Dependencies and integration points: used by object-specific local/policy headers, generic database method tables, direct commit validators, `semanage.h`, man pages, and SWIG wrapping. Context-bearing records integrate with `context_record.h`.

Risks: callers must not free borrowed getter strings or nested context pointers unless the API documents ownership through an output allocation. Range/protocol/type constants must stay ABI-stable. Test signals include key equality ordering, clone independence, setter validation, round-trip parse/print, and correct cleanup on allocation failure.
