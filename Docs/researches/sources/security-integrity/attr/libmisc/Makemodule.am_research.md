## sources/security-integrity/attr/libmisc/Makemodule.am

Purpose: build fragment for private utility library `libmisc.la`.

It collects allocation, line reading, quoting, unquoting, and traversal helpers used by attr tools. State is build artifacts only. Dependencies are top-level Automake and source files. Risks are all helpers sharing one private library without independent tests. Test signal is successful linking of `attr`, `getfattr`, and `setfattr`.
