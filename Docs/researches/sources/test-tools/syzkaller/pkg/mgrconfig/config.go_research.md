# sources/test-tools/syzkaller/pkg/mgrconfig/config.go

Purpose: Defines the syz-manager JSON configuration schema and derived runtime fields used across manager, VM, report, corpus, dashboard, hub, coverage, and experimental systems.

Important types: `Config` contains user-provided fields such as `name`, `target`, `http`, `rpc`, workdir paths, kernel object/source paths, VM image and SSH settings, hub/dashboard settings, syzkaller checkout, procs, sandbox, snapshot/coverage/repro flags, syscall filters, suppressions/interests, strace/executor-on-target settings, asset storage, memory dumps, VM type/raw config, and embedded `Experimental` plus `Derived`. `Experimental` includes reset accumulated state, remote coverage, edge coverage, descriptions mode, focus areas, and KFuzzTest. `FocusArea`, `Subsystem`, and `CovFilterCfg` model coverage and subsystem filters.

Control flow and state: This file defines data only; loading, defaults, validation, and derived field population happen in `load.go`.

Dependencies and integration: Imported by nearly every manager package. JSON tags form the external config contract. `asset.Config` integrates crash asset upload configuration.

Risks: Schema changes affect user configs, canned tests, dashboard/hub behavior, and VM-type-specific parsing. Some fields are deprecated (`CovFilter`) or experimental and may have compatibility concerns. Misdocumented path semantics could cause coverage/report failures.

Test signals: `mgrconfig_test.go` loads canned configs into this schema and VM-specific schemas.
