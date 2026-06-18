# sources/sync-backup/git-lfs/script/gen-i-reverse

Purpose: generates a pseudo-translation file by reversing words in gettext `msgid` strings, useful for i18n layout/testing.

Important functions/state: global parser state `:idle`, `:copy`, `:msgid`, `:msgid_multi`, `:msgid_plural_multi`; `reset_state`; `translate`.

Control flow: validates input/output arguments, then streams a PO-like file line by line. It copies empty msgids, captures singular/plural msgids including xgotext backtick-delimited multiline strings, and fills empty `msgstr` entries with reversed translated text while preserving printf-style chunks beginning with `%`.

State/persistence behavior: writes the output file incrementally and stores current singular/plural message state in globals.

Dependencies/integration: used by localization/test tooling around generated gettext catalogs.

Risks: parser is intentionally narrow and uses globals. It assumes specific PO syntax and can silently omit unexpected line forms. It fixes nonstandard backtick strings from xgotext rather than implementing a complete PO parser.

Test signals: no direct tests in this subset; useful signals are generated msgstr entries, preserved placeholders, and valid output syntax.
