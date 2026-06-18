<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/reg_util_internal.h -->
# sources/user-network-fs/samba/source3/registry/reg_util_internal.h

Purpose: Internal header declaring registry path utility functions.

Important APIs, types, and functions: Declares `reg_split_path()`, `reg_split_key()`, `normalize_reg_path()`, and `reg_remaining_path()`.

Control flow: No executable logic. The prototypes expose both destructive split helpers and talloc-allocating normalization helpers.

State and persistence behavior: No header-owned state. Callers must respect that split results alias the modified input buffer, while normalized results live under caller-provided talloc contexts.

Dependencies and integration points: Included by registry frontend and backend modules that need consistent registry path manipulation.

Risks: The include guard name `_REG_UTIL_H` is generic and could collide with similarly named registry utility headers. The API does not encode ownership or mutation in the type signatures.

Test signals: Compile coverage for all registry utility consumers and path-behavior tests through `reg_util_internal.c`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/reg_util_internal.h -->
