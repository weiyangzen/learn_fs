## sources/security-integrity/attr/man/man1/Makemodule.am

Purpose: declares command manpages for distribution/install.

It adds `attr.1`, `getfattr.1`, and `setfattr.1` to `dist_man_MANS`. State is packaging metadata only. Dependencies are top-level man aggregation. Risks are CLI behavior drifting from documentation. Tests are distribution/install checks.
