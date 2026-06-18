# sources/test-tools/syzkaller/pkg/coveragedb/bq-schema.json

Purpose: declares the BigQuery ingestion schema for manager coverage records emitted by `manager_to_ci.go`.

Important fields: required metadata fields `timestamp`, `version`, `fuzzing_minutes`, `arch`, `build_id`, `manager`, `kernel_repo`, `kernel_branch`, `kernel_commit`; source-location fields `file_path`, `func_name`, `sl`, `sc`, `el`, `ec`; coverage fields `hit_count`, `inline`, and `pc`. `pc` is NUMERIC with precision 20 and scale 0 to store full 64-bit-ish PC values.

Control flow: not executable. Its field names align with `CoverageInfo`, `CIDetails`, `covermerger` CSV keys, and BigQuery export queries.

State and persistence: schema governs persistent BigQuery table layout outside the repo.

Dependencies and integration: consumed operationally when creating/updating the `syzkaller.syzbot_coverage.<namespace>` BigQuery tables. `covermerger.InitNsRecords` queries many of these field names.

Risks: descriptions mention "fuzzing hours" while field name says minutes. Typos in descriptions (`StarCol`) are harmless but confusing. Any schema change must be coordinated with manager JSONL output and `covermerger` CSV parser keys.

Test signals: no direct schema test; `manager_to_ci_test.go` and `covermerger` CSV tests indirectly protect selected field names.
