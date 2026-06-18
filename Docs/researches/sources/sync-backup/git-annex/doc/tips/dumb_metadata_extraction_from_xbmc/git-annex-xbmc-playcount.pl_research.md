<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-annex/doc/tips/dumb_metadata_extraction_from_xbmc/git-annex-xbmc-playcount.pl -->
# sources/sync-backup/git-annex/doc/tips/dumb_metadata_extraction_from_xbmc/git-annex-xbmc-playcount.pl

Purpose: Perl helper that reads XBMC/Kodi video database play counts and writes them to git-annex metadata as `playCount=<count>`.

Important functions: `checkargs` parses `--annex`, `--path`, `--home`, `--dryrun`, and `--verbose` with `Getopt::Long` and uses `Pod::Usage` for help. `finddb(path)` scans for `MyVideos*.db` and returns the newest by modification time. `checkdb` runs a SQLite query joining `movie`, `files`, and `path`, parses `playCount|strPath|strFileName` rows, handles `stack://` multi-file entries, strips the configured annex prefix, and either prints or executes `git annex metadata --set playCount=<count> <file>`.

Control flow: `main` resolves the database directory, finds a database, and processes every movie row. Dry-run mode prints shell-like commands instead of invoking git-annex.

State and persistence: writes git-annex metadata when not in dry-run mode. It reads the XBMC SQLite DB through the `sqlite3` command and does not modify the DB.

Dependencies and integration points: Perl, `Getopt::Long`, `Pod::Usage`, external `sqlite3`, `git annex metadata`, XBMC/Kodi database schema, and repository-relative path conventions.

Risks: the SQL output is parsed by splitting on `|`, and the POD explicitly notes filenames containing pipes can break parsing. `finddb` returns no database when exactly one file is found because it checks `$#flist > 0`, which requires at least two entries; this looks like a bug. Paths are manipulated with regex substitutions using the `--annex` value, which can behave unexpectedly if it contains regex metacharacters. System command exit codes are not checked.

Test signals: unit-test `finddb` with one and multiple DB files, dry-run against a fixture SQLite database, stacked and non-stacked paths, paths containing pipes/spaces, and nonzero git-annex failures.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-annex/doc/tips/dumb_metadata_extraction_from_xbmc/git-annex-xbmc-playcount.pl -->
