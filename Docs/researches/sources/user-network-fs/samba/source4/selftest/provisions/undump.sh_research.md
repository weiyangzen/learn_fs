<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/provisions/undump.sh -->
# sources/user-network-fs/samba/source4/selftest/provisions/undump.sh

Purpose: restores provision `.dump` files back to `.tdb` or `.ldb` database files using `tdbrestore`.

Important APIs/types/functions: arguments `<DIRECTORY> [TARGETDIR] [TDBRESTORE]`, `find`, `tdbrestore`, target directory creation, and output replacement.

Control flow: validates input, selects restore command, changes into dump directory, sets target dir, loops over `.dump` files, derives output filename by removing `.dump`, removes existing output, restores from dump content, and exits.

State and persistence behavior: creates/restores DB files in the target tree and removes any existing output file before restore.

Dependencies and integration points: paired with `dump.sh` for checked-in provision fixtures.

Risks: unquoted loop breaks on paths with spaces. Existing DB files are removed before restore. Partial restores can leave mixed state after failure.

Test signals: restored `.tdb`/`.ldb` files and successful `tdbrestore` exit codes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/provisions/undump.sh -->
