# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/log.c

Purpose: appends gettext-style untranslated-message entries to a log file. It is used when translation lookup fails and logging is enabled elsewhere in libintl.

Important APIs and control flow: `_nl_log_untranslated(logfilename, domainname, msgid1, msgid2, plural)` caches the last opened filename and `FILE *`, reopening only when the target changes. It emits `domain`, `msgid`, optional `msgid_plural`, and an empty `msgstr`/`msgstr[0]` block. `print_escaped()` quotes ASCII strings, escaping backslash and double quote, and splits embedded newlines into PO-style continued strings.

State and persistence: static `last_logfilename` and `last_logfile` persist across calls; file contents are appended with `fopen(..., "a")`. There is no explicit flush after each entry and no lock protection.

Dependencies and integration: depends on stdio/stdlib/string and is called from gettext failure paths. Output format is intended to be consumable as PO fragments.

Risks and test signals: not thread-safe, silently drops entries on allocation/open failure, and keeps descriptors open until another filename is used or process exit. Test escaped quotes, backslashes, trailing and non-trailing newlines, plural entries, filename switches, and open failure behavior.
