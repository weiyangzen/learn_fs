# sources/sync-backup/kopia/internal/metricid/id_mapping_test.go

Purpose: verifies generic map/slice conversion behavior for metric ID mappings.

Important APIs/types/functions: `metricid.NewMapping`, `MapToSlice`, and `SliceToMap`.

Control flow: `TestMapToSlice` builds a mapping with a gap, checks nil and partial maps, verifies the gap is represented by a zero value, and confirms unknown key `c` is dropped. `TestSliceToMap` checks short, exact, and overlong slices, ensuring only mapped indexes appear in the result.

State/persistence behavior: no durable state. The tests model compact persisted JSON shapes where slice positions correspond to metric IDs.

Dependencies/integration: uses `testify/require` and package `metricid_test`, covering exported behavior only.

Risks/test signals: tests do not cover duplicate or zero IDs in mappings; built-in mapping validation handles part of that separately.
