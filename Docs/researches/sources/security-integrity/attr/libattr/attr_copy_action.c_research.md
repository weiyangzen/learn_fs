## sources/security-integrity/attr/libattr/attr_copy_action.c

Purpose: parse and apply `/etc/xattr.conf` copy policy.

It defines a linked list of `attr_action` patterns, lazy-loads `SYSCONFDIR/xattr.conf`, supports `skip` and `permissions` actions, and returns the first `fnmatch` action for an xattr name. State persists globally in `attr_actions` until parse failure or process exit. Dependencies are stdio allocation, `fnmatch`, `error_context`, and install-time `SYSCONFDIR`. Risks include global non-thread-safe lazy initialization, entire-file read with doubling size, reverse order because new actions prepend, parse strictness around whitespace/comments, and generic error messages that quote only the config path. Tests should cover missing config, malformed lines, wildcard precedence, and action lookups.
