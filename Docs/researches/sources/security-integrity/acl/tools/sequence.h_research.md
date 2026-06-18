## sources/security-integrity/acl/tools/sequence.h

Purpose: data model and command constants for `setfacl` edit sequences.

It defines `struct cmd_obj` fields for command kind, ACL type/tag/id/permissions, and next pointer, plus `struct seq_obj` head/tail pointers. Constants describe replace, remove-entry, remove-extended, and remove-ACL actions and permission bits including conditional execute. This header is the integration point between parsing, CLI construction, and the lower-level `do_set` executor. State/persistence is in-memory only. Risks are exposed struct internals that encourage cross-module mutation and numeric command values coupled to executor assumptions. Tests should cover every command constant through actual `setfacl` operations.
