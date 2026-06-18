# sources/security-integrity/selinux/libsemanage/src/parse_utils.h

Purpose: declares the shared parsing state and helper APIs used by file-backed record parsers.

Important types/APIs: `parse_info_t` stores line number, original/working line buffers, current pointer, filename, file stream, and caller parse argument. It declares lifecycle, stream, whitespace/comment skipping, assertion, optional token, integer, and string fetch helpers.

Control flow/integration: `*_file.c` parsers receive a `parse_info_t`, call `parse_skip_space`, then consume tokens using this API. `parse_arg` allows backend-specific auxiliary state, although these files mostly do not use it.

State/persistence: no persistent state beyond parser fields. Risks include the typo in the declaration parameter name `hgandle`, which is harmless but can confuse readers, and callers needing to respect ownership of fetched strings. Test signals are compile coverage and parser tests for all database text formats.
