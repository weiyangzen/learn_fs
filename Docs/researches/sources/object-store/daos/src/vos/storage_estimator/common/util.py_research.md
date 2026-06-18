# sources/object-store/daos/src/vos/storage_estimator/common/util.py

## Purpose
Shared utility layer for the DAOS VOS storage estimator. It handles logging/formatting, object-class validation, metadata loading, CLI numeric parsing, checksum/chunk/scm-cutoff processing, conversion from DFS exploration to estimator YAML, and invoking `MetaOverhead`.

## Important APIs, types, and functions
- `CommonBase` provides verbose output, human-readable size parsing/formatting, positive integer checks, and suffix handling.
- `ObjectClass` validates supported object classes (`S1`, `SX`, `RP_3GX`, `EC_16P2GX`, etc.) and exposes target/stripe/parity/replica parameters.
- `Common` loads VOS metadata from `VOS_SIZE`, reads/writes YAML, and runs `_process_yaml`.
- `ProcessBase` combines `Common` with object-class and DFS/CSV processing: block sizes, checksum selection, shard validation, aggregation assumptions, and `Containers` construction.
- Integration objects include `MetaOverhead`, `get_dfs_sb_obj`, and `VOS_SIZE`.

## Control flow
CLI command classes inherit `Common` or `ProcessBase`. Construction loads VOS metadata, parses object class and sizing options, validates EC constraints, applies optional metadata override, then later `run()` either loads user YAML or converts an explored/CSV model to YAML. `_process_yaml` instantiates `MetaOverhead`, loads every container, and prints a report.

## State and persistence behavior
Instances hold parsed args, verbosity, VOS metadata YAML, object-class state, checksum size, SCM cutoff, I/O size, chunk size, EC cell size, and shard count. `_create_file` persists generated YAML/metadata files. The estimator itself is read-only except for optional output files.

## Dependencies and integration points
Depends on PyYAML, `storage_estimator.dfs_sb`, `storage_estimator.vos_size`, `storage_estimator.vos_structures`, and generated VOS metadata from a DAOS storage path. It is the common integration point for `daos_storage_estimator.py`, filesystem exploration, CSV processing, and direct YAML reads.

## Risks and edge cases
`_from_human` accepts loose suffixes by stripping suffix letters, which can parse surprising strings. `ObjectClass._update_oclass` ignores its `default_value` parameter and requires the arg value to already be supported. EC validation is strict about chunk/stripe/cell divisibility. `_load_yaml_from_file` opens without an explicit context manager. Some checks use `'average' in self._args`, which is not normal for `argparse.Namespace` unless customized elsewhere.

## Test signals
Signals include correct parsing of human sizes, rejection of invalid object classes/shard counts/EC arguments/checksum names, successful YAML loading and report printing, and stable generated YAML for filesystem or CSV inputs.
