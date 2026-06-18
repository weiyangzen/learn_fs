# sources/sync-backup/rsync/latest-year.h

Purpose: centralizes the latest copyright/help year string for rsync-generated output.

Important APIs/types/functions: defines `LATEST_YEAR` as the string literal `"2026"`.

Control flow: no executable logic.

State and persistence behavior: no state or persistence. The macro is compile-time text consumed by other rsync sources.

Dependencies/integration: integrated wherever rsync prints version, copyright, or generated usage text that should carry the current project year.

Risks/test signals: the only practical risk is staleness. Release/build checks can grep generated version/help output for the expected year.
