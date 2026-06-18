<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/nfsdclddb/nfsdclddb.py -->
# sources/user-network-fs/nfs-utils/tools/nfsdclddb/nfsdclddb.py

## Purpose

`nfsdclddb.py` inspects and repairs the sqlite database used by `nfsdcld` for NFSv4 client recovery epochs. It can print database summary/client records, repair short recovery table names, and downgrade schema version 4 tables to version 3 by dropping principal hash data.

## Important APIs, Types, and Functions

`CldDb` opens the sqlite database, reads `parameters.version` and the `grace` epoch row, and exposes print, validation, repair, and downgrade methods. `_print_clients` prints ids and, for schema v4, `princhash`. `check_bad_table_names` finds malformed `rec-*` table names; `fix_bad_table_names` renames tables matching current/recovery epochs and drops unknown short tables. `has_princ_data`, `_downgrade_table_v4_to_v3`, and `downgrade_schema_v4_to_v3` implement guarded v4-to-v3 migration. Command handlers add active-daemon warnings.

## Control Flow

`main` builds argparse subcommands, defaults no-argument invocation to `print --summary`, verifies the database path exists, constructs `CldDb`, and dispatches the selected handler. Repair and downgrade commands warn if `nfsdcld` appears in `ps -C`, ask for confirmation, then run exclusive sqlite transactions.

## State and Persistence Behavior

Print mode is read-only. `fix_bad_table_names` mutates sqlite schema names and may drop unknown malformed tables. Downgrade creates replacement epoch tables with only `id`, drops v4 tables, renames replacements, and updates `parameters.version` to `3`, committing or rolling back as one transaction.

## Dependencies and Integration Points

The script depends on Python `sqlite3`, `/var/lib/nfs/nfsdcld/main.sqlite` by default, the `parameters`, `grace`, and `rec-%016x` schema, and the external `nfsdcld` service. It is an offline administrative companion to the NFSv4 server client recovery daemon.

## Risks and Edge Cases

`__init__` assumes version and grace rows exist. `has_princ_data` appears to query the current epoch twice when recovery is present, which can miss principal data in the recovery table. SQL uses formatted table names from trusted database metadata and epoch values; malformed names are partly handled by the repair command. The daemon-active check uses `ps -C`, which is heuristic. If a command is omitted but arguments are not empty, `args.func` may be absent.

## Test Signals

Tests should use temporary sqlite databases for v3 and v4 schemas, current-only and current+recovery epochs, malformed short table names, unknown epoch tables, rollback on injected sqlite errors, principal-data warnings, default summary behavior, and missing-path usage output.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/nfsdclddb/nfsdclddb.py -->
