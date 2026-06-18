## sources/security-integrity/attr/po/update-potfiles

Purpose: regenerate gettext source file list.

The script writes `po/POTFILES.in` with a generated header and sorted `*.[ch]` files under include, libattr, libmisc, and tools, excluding generated `include/config.h`. State is the updated POTFILES file. Dependencies are shell, `find`, `grep`, `sort`, and locale sorting. Risks include excluding non-C translatable files and overwriting manual POTFILES edits. Test signal is running before gettext extraction and ensuring all `_()` call sites are included.
