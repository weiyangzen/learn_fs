# sources/user-network-fs/samba/source3/torture/test_matching.c

Purpose: This file tests Samba path matching utilities for MS wildcard lists and regular-expression-with-one-substitution lists. It compares legacy matching behavior with the newer `samba_path_matching` abstraction and validates match indexes and replacement spans.

Important APIs/types/functions: `run_str_match_mswild()` exercises `set_namearray()`, `is_in_path()`, `samba_path_matching_mswild_create()`, and `samba_path_matching_check_last_component()`. `run_str_match_regex_sub1()` exercises `samba_path_matching_regex_sub1_create()` and checks invalid regex lists. Data tables encode expected match indexes for case-sensitive and case-insensitive modes plus expected regex subgroup start/end offsets.

Control flow: The MS wildcard test creates both case-sensitive and case-insensitive matchers from `/abc*.txt/xyz*.dat/a0123456789Z/`, iterates representative paths, compares legacy boolean membership with matcher index output, and requires no replacement span. The regex test first asserts that malformed lists return `NT_STATUS_INVALID_PARAMETER`, then creates a valid matcher and checks path matches plus the first captured subgroup offsets.

State/persistence behavior: This is an in-memory utility test. Matchers and name arrays are talloc-owned; there is no file, network, or persistent cache state. Diagnostic output goes to stderr.

Dependencies and integration points: It depends on `lib/util_matching.h`, torture prototypes, `SMB_ASSERT`, and Samba string/path matching utilities used by include/exclude and path rewrite style configuration.

Risks: The tests assert on many setup failures, so malformed matcher behavior can abort rather than return false. Regex offset expectations are byte-index based and depend on last-component matching semantics; changes in path normalization or regex dialect will require updating the fixture table.

Test signals: Passing requires expected indexes for all wildcard samples, rejection of four invalid regex lists, expected match indexes for valid regex samples, and exact captured replacement start/end offsets.
