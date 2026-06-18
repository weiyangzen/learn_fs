# sources/security-integrity/cryfs/crates/utils/src/data/data.rs

Purpose: owned byte buffer with a logical region window, enabling copy-free shrinking to subregions while retaining ownership.

Important APIs/types/functions: `Data { storage: Vec<u8>, region: Range<usize> }`; `allocate`, `empty`, `len`, `shrink_to_subregion`, `grow_region`, `grow_region_fail_if_reallocation_necessary`, `reserve`, `append_writer`, prefix/suffix availability, `resize`, `into_vec`; `DataAppendWriter` implements `Write`.

Control flow: shrinking translates bounds relative to current region and updates `region`; growing either reserves/reallocates or fails if slack is insufficient. Accessors expose only `storage[region]`. Append writer extends region then copies bytes into the new suffix.

State/persistence: in-memory byte storage. Subregions keep the original allocation alive, which avoids copies but can retain large buffers.

Dependencies/integration: used for data-block manipulation, likely in filesystem/encryption layers. Tests use `DataFixture`.

Risks: invalid ranges panic via invariant assertions. Retained hidden prefix/suffix may waste memory. Several methods are marked TODO for tests.

Test signals: many unit tests cover empty/full data, range forms, nested subregions, availability counts, and out-of-bounds/inverted range panics.
