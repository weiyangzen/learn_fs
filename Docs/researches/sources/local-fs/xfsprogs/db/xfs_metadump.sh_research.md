# File Research: sources/local-fs/xfsprogs/db/xfs_metadump.sh

Shell wrapper for running `xfs_db` metadump mode.

Key responsibilities:
- Parses metadump options and translates them into `xfs_db` options plus a `metadump` command.
- Supports source and target operands.
- Delegates `-V` to `xfs_db`.

Important behavior:
- Runs `xfs_db -i -p xfs_metadump -c "metadump... target" source`.
- Passes log/realtime/force/debug-ish options through DB option variables.

Dependencies:
- External `xfs_db`.

Notable risks:
- Option strings are assembled with shell concatenation and unquoted expansions, so unusual filenames/options can be fragile.
