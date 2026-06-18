<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/ext/test_checkpoint_meta_version.cpp -->
# sources/storage-engines/wiredtiger/test/catch2/ext/test_checkpoint_meta_version.cpp

Purpose: Tests disaggregated checkpoint metadata version parsing and compatibility validation.

Important APIs/types/functions: Fixture builds a mock session; tests call `__ut_disagg_validate_checkpoint_meta_version` and compare `version`/`compatible_version` with `WT_DISAGG_CHECKPOINT_META_VERSION_DEFAULT`.

Control flow: Sections parse explicit version pairs, missing fields, only one field, forward-incompatible versions, illegal compatible-version newer than version, and multiple incompatible configs.

State and persistence behavior: Local mock session and output integers only; no persistent metadata write.

Dependencies and integration points: Covers extension/disaggregated metadata compatibility logic used when reading checkpoint metadata strings.

Risks and test signals: Forward compatibility checks must distinguish `ENOTSUP` from invalid config `EINVAL`. Signals are defaulting behavior for old metadata and rejection of too-new reader requirements.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/ext/test_checkpoint_meta_version.cpp -->
