# sources/object-store/daos/src/vos/tests/vos_size_input.yaml

## Purpose
Human-readable sample input for the VOS storage-size estimator. It documents the YAML schema and provides a small nested example with containers, objects, dkeys, akeys, and values.

## Important APIs, types, and functions
- `num_shards: 30` sets VOS pool count.
- Example value anchors define extent and single-value records.
- Example akeys demonstrate array and single-value `value_type`, hashed/integer key types, and multiple values.
- Example dkey/object/container anchors demonstrate count multiplication and checksum settings.

## Control flow
No executable flow. The estimator reads this file through `read_yaml`, validates required fields, loads it into `MetaOverhead`, and prints totals.

## State and persistence behavior
Declarative only. It models 10 identical containers, each with 100 objects, each with 200 integer dkeys, and akeys/values multiplied by their counts. Container checksum size/granularity is set to 64 and 4096.

## Dependencies and integration points
It is sample documentation and an input fixture for `daos_storage_estimator.py read_yaml`. It depends on the schema enforced by `vos_size.py`.

## Risks and edge cases
Because it is both documentation and input, comments must stay aligned with code defaults. Counts multiply quickly, so small edits can have large output impact. It does not demonstrate every field, such as explicit `overhead` on each node.

## Test signals
Signals are successful parse and a plausible estimator breakdown that exercises array values, single values, checksum overhead, integer keys, and count multiplication.
