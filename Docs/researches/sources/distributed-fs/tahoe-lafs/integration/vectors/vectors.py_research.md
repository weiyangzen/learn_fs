# sources/distributed-fs/tahoe-lafs/integration/vectors/vectors.py

## Purpose

This module loads and saves persisted integration test vectors for Tahoe-LAFS capability generation. It provides a small serialization layer around YAML test data, keeping byte strings JSON/YAML-safe with base64 and reconstructing `Case` objects that combine erasure-coding parameters, convergence secrets, sample data, object format, and expected capabilities.

## Important APIs, Types, and Functions

`DATA_PATH` points at sibling `test_vectors.yaml`, and `CURRENT_VERSION` gates compatibility with the persisted file. The frozen `Case` attrs class is the key domain type; its `data` property expands a seed into deterministic bytes via `stretch`, and `params` realizes abstract `SeedParam` values against the selected `CHK` or `SSK` format. `encode_bytes` and `decode_bytes` are the base64 transport helpers. `save_capabilities` writes a versioned YAML document from `(Case, capability)` pairs. `load_format` dispatches serialized format records to `CHK.load` or `SSK.load`, and `load_capabilities` validates the version then returns a `dict[Case, str]`.

## Control Flow

On import, the module tries to open `DATA_PATH` and initializes the module global `capabilities`; missing files produce an empty dict. Loading calls `yaml.safe_load`, treats an empty YAML document as no vectors, rejects mismatched versions by printing a diagnostic and returning `{}`, then builds `Case` keys from each vector entry. Saving performs the inverse transformation, deriving `required` and `total` from `case.params`, not directly from `seed_params`.

## State, Dependencies, Integration, Risks, and Tests

State is file-backed only when `save_capabilities` is called; import-time `capabilities` is an in-memory snapshot. Dependencies are `attrs`, PyYAML, Twisted `FilePath`, and local vector model/format classes. Integration points are the integration tests that compare generated capabilities with persisted expectations. Risks include import-time I/O, silent empty results on version mismatch, assertions in `stretch` being removable under optimized Python, and a requirement that `Case` remains hashable because it is used as a dict key. Test signals should cover round-trip save/load, unknown format errors, version mismatch behavior, base64 byte preservation, deterministic stretch output, and missing/empty YAML files.
