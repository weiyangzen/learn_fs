## sources/security-integrity/attr/tools/Makemodule.am

Purpose: build fragment for attr command-line tools.

It defines common link dependencies on `libattr.la`, `libmisc.la`, and gettext, then builds `attr`, `getfattr`, and `setfattr`. State is built binaries. Dependencies are attr private/public libraries and top-level toolchain variables. Risks are all tools sharing private helper semantics and static buffers. Test signal is `make check` transcript coverage.
