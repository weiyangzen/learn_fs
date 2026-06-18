# sources/object-store/daos/src/vos/vos_size.c

## Purpose
`vos_size.c` generates YAML describing VOS metadata structure and tree overhead sizes for use by `vos_size.py` and related capacity-estimation tooling. It initializes VOS locally, asks runtime tree classes for overhead, and prints aligned records plus checksum sizes.

## Important APIs, Types, And Functions
The primary function is `get_vos_structure_sizes_yaml`. Helper macros enumerate container, object, dkey, akey, integer-key variants, single-value, array, and VEA overhead classes. `print_dynamic` and `print_record` format tree overhead data, while `get_daos_csummers` initializes all DAOS hash algorithms and records checksum lengths.

## Control Flow
The generator clears the output buffer, initializes DAOS debug and VOS self state, calls `vos_tree_get_overhead` for each tree type, writes root/container/SCM cutoff values, emits dynamic node references and tree records, emits checksum sizes, handles string-buffer errors, and tears VOS/debug state down.

## State And Persistence
There is no durable VOS state change intended. Runtime initialization may create or access local VOS self state at the supplied path, and all output is accumulated in a `d_string_buffer_t`.

## Dependencies And Integration Points
The file depends on `vos_overhead.c`, VOS self init/fini, DAOS debug setup, DAOS checksum algorithms, and string-buffer helpers. It is tooling-facing rather than data-path-facing, but its output should track real VOS tree allocation behavior.

## Risks
Risk comes from failing to initialize VOS self state, checksum algorithm initialization failures, buffer allocation/write errors, and drift between `FOREACH_TYPE` and supported tree classes. Alignment to 32 bytes is baked into reporting and should remain consistent with allocator expectations.

## Test Signals
Tests should assert that YAML generation succeeds for a valid VOS path, includes all expected tree keys and checksum algorithms, handles initialization failure cleanly, and changes when underlying tree overhead constants change.
