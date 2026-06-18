# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/ngettext.c

Purpose: implements the public plural gettext entry point for the current default domain.

Important APIs and control flow: `NGETTEXT(msgid1, msgid2, n)` is name-mapped to `__ngettext` for glibc or `libintl_ngettext` for standalone libintl. The function delegates all real lookup and plural selection to `DCNGETTEXT(NULL, msgid1, msgid2, n, LC_MESSAGES)`. A glibc weak alias exposes `ngettext`.

State and persistence: this file stores no state. It relies on global gettext domain, locale, catalog cache, and plural-expression state managed by other libintl files.

Dependencies and integration: includes `gettextP.h`, either system `libintl.h` or local `libgnuintl.h`, and `locale.h`. It is a thin integration wrapper connecting the standard API to `dcngettext`.

Risks and test signals: risks live in downstream lookup logic, but this wrapper must preserve ABI names and category selection. Test that `ngettext` honors the current `textdomain`, `LC_MESSAGES`, and plural `n`, and that default fallback returns `msgid1`/`msgid2` when no catalog exists.
