<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/provisions/dump.sh -->
# sources/user-network-fs/samba/source4/selftest/provisions/dump.sh

Purpose: converts `.tdb` and `.ldb` files in a provision directory into `.dump` text files using `tdbdump`.

Important APIs/types/functions: arguments `<DIRECTORY> [TARGETDIR] [TDBDUMP]`, `find`, `tdbdump`, target directory creation, and source DB file removal.

Control flow: validates input, selects `tdbdump` command, changes into the provision directory, sets target directory, dumps each `.tdb` and `.ldb` file to a mirrored `.dump` path, removes the original DB file after successful dump, and exits.

State and persistence behavior: destructive conversion: original database files are removed after dump files are created.

Dependencies and integration points: paired with `undump.sh` for storing provision fixtures in dump form.

Risks: unquoted `find` loop breaks on spaces. Running against a live or valuable provision removes DB files. Errors abort after partial conversion.

Test signals: `.dump` files in the target tree and absence of original `.tdb`/`.ldb` files.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/provisions/dump.sh -->
