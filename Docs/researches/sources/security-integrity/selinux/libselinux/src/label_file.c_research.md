# sources/security-integrity/selinux/libselinux/src/label_file.c

Purpose: Implements the file-context labeling backend. It loads text or compiled `file_contexts` data into a stem tree of literal and regex specs, supports substitutions, lookup, partial-match digesting, stats, and handle comparison.

Important APIs/types/functions: entrypoint `selabel_file_init()` installs close/stats/lookup/partial/digest/best-match/cmp callbacks. Major internals include `process_text_file()`, `load_mmap()`, `merge_mmap_spec_nodes()`, `process_file()`, substitution init/apply helpers, `lookup_all()`, `lookup_check_node()`, `lookup_best_match()`, `hash_all_partial_matches()`, `cmp()`, and `free_spec_node()`. Data structures are from `label_file.h`: `spec_node`, `literal_spec`, `regex_spec`, `saved_data`, and `mmap_area`.

Control flow: init parses `SELABEL_OPT_PATH`, `SUBSET`, and `BASEONLY`, loads substitution files, then loads base, optional homedirs, and local file contexts. Each source is opened as newest text/bin candidate, with fallback to oldest if processing fails. Text lines are parsed by `process_line()` into literal or regex specs and inserted into a bounded-depth stem tree. Compiled files are mmaped, validated for magic/version/regex version/architecture, loaded into tree nodes, and merged. Lookups normalize duplicate/trailing slashes, apply substitutions, find the deepest stem node, prefer literal matches, then regex matches in reverse input order and parent precedence, honoring file kind and `<<none>>`.

State and persistence: handle owns tree allocations, mmap areas, substitutions, digest, match flags, and lazily compiled regex data. It reads but does not modify spec files; partial-match digest compares with `security.sehash` xattr.

Dependencies and integration: depends on regex backend abstraction, SHA1, xattr, file context suffixes, label frontend, and validation callback.

Risks and test signals: high-risk areas are mmap binary parsing bounds, regex lazy compilation, spec priority, substitution order, duplicate detection, and partial-match digest compatibility. Tests should cover text/bin loading, version mismatch fallback, `file_contexts.local` priority, subset filtering, literal vs regex precedence, `<<none>>`, malformed compiled data, compare subset/superset, and restorecon digest behavior.
