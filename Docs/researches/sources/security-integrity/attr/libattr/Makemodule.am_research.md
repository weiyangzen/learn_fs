## sources/security-integrity/attr/libattr/Makemodule.am

Purpose: build fragment for `libattr.la`.

It defines libtool versioning, gettext linkage, exports dependency, source list, Linux-only syscall compatibility wrappers, compile injection of `libattr/libattr.h`, and linker version script flags. State is library ABI metadata and built shared/static artifacts. Dependencies include libtool, `exports`, gettext, and Linux conditional. Risks include ABI/version-script coupling and forced include behavior affecting every source. Test signals are library link, symbol version inspection, and downstream tool linkage.
