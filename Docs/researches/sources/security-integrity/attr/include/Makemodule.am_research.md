## sources/security-integrity/attr/include/Makemodule.am

Purpose: Automake install logic for public and private attr headers.

It lists headers, defines `SUBST_INSTALL_HEADER` to replace `EXPORT` with `extern` into temporary generated headers, installs public `attributes.h`, `error_context.h`, and `libattr.h`, and removes them on uninstall. State is generated `include/*.t` during install and installed header files. Dependencies are `sed`, install helpers, and top-level `pkgincludedir`. Risks include regex portability for `\<EXPORT\>` and install-time temporary-file cleanup. Test signals are `make install` and inspecting installed headers for correct `extern` declarations.
