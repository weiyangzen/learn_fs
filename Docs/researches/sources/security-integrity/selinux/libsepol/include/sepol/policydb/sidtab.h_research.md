# sources/security-integrity/selinux/libsepol/include/sepol/policydb/sidtab.h

Purpose: Defines the internal security identifier table mapping SIDs to context structures.

Important APIs and types: `sidtab_node_t`, `sidtab_t`, hash constants, and functions for init, insert, search, map, map-remove-on-error, context-to-SID allocation/lookup, hash eval, destroy, set, and shutdown.

Control flow: Service code loads initial SIDs, resolves contexts to existing or newly allocated SIDs, and searches by SID during access decisions and context conversion.

State and persistence: Sidtab owns hash buckets of SID/context copies, next SID counter, element count, and shutdown flag. It is runtime state, not the policydb itself.

Dependencies and integration points: Depends on internal context representation and Flask SID types; used by services and policy loading.

Risks: Context equality/copy and next_sid allocation must avoid duplicate or invalid SIDs. Shutdown behavior affects dynamic SID allocation.

Test signals: Insert/search, context-to-SID duplicate detection, map removal on callback failure, destroy, and shutdown tests validate it.
