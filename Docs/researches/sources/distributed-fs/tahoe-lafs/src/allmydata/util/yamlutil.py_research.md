# sources/distributed-fs/tahoe-lafs/src/allmydata/util/yamlutil.py

## Purpose

This module provides a tiny safe YAML import surface. It keeps Tahoe callers on `yaml.safe_load` and `yaml.safe_dump` instead of the unsafe default loader/dumper APIs.

## APIs and control flow

`safe_load(f)` delegates to `yaml.safe_load(f)`. `safe_dump(obj)` delegates to `yaml.safe_dump(obj)`. There is no additional validation, state, or branching. The wrapper centralizes import paths and makes intent explicit.

## State, dependencies, risks, and tests

There is no local state or persistence; YAML documents are caller-owned. The only dependency is PyYAML. Integration is any Tahoe code that reads or writes YAML configuration or metadata.

Risks include assuming this wrapper enforces schema validation; it only uses PyYAML's safe constructors. `safe_load()` may return `None` for empty input, and `safe_dump()` formatting is PyYAML-version dependent. Test signals should cover simple maps/lists/scalars, rejection of unsafe constructors, empty documents, round-trip expectations where order/format does not matter, and caller handling of `None`.
