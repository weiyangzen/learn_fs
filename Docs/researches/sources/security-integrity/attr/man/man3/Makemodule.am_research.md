## sources/security-integrity/attr/man/man3/Makemodule.am

Purpose: declares library API manpages.

It adds man3 pages for `attr_get`, `attr_list`, `attr_multi`, `attr_remove`, and `attr_set`. Integration with the parent install hook creates aliases for multi-function pages. Risks are deprecated API documentation drift. Test signal is `make distcheck` and installed manpage alias coverage.
