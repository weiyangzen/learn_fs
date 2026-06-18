# sources/security-integrity/selinux/libsepol/include/sepol/policydb/mls_types.h

Purpose: Defines internal MLS levels, ranges, semantic category ranges, and inline MLS operations.

Important APIs and types: `mls_level_t`, `mls_range_t`, semantic cat/level/range structs; inline dominance/equality/between/contains/copy/destroy/GLB-LUB helpers; exported semantic init/destroy/copy functions.

Control flow: MLS checks compare sensitivities and category ebitmaps. Semantic structures from policy source are expanded into numeric `mls_level_t`/`mls_range_t`.

State and persistence: MLS levels own category ebitmaps. Ranges are stored in contexts, users, constraints, and range transitions.

Dependencies and integration points: Depends on ebitmap, Flask types, and system min/max helpers; used by context validation and expansion.

Risks: Dominance and GLB/LUB logic is security-critical. Copy failures must destroy partially copied category bitmaps.

Test signals: Range containment, incomparable levels, overlapping/non-overlapping GLB/LUB, semantic copy/destroy, and context MLS validation are essential.
