<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-config/src/version.rs -->
# sources/security-integrity/cryfs/crates/cryfs-config/src/version.rs

Purpose: defines this crate's CryFS version constant.

Important APIs/types/functions: `CRYFS_VERSION` is assigned from `cryfs_version::CRYFS_VERSION`.

Control flow: no runtime flow. Loader compares this version against supported filesystem format bounds and CLI displays it.

State and persistence: version string may be written into `created_with_version` and `last_opened_with_version` fields by creator/loader.

Dependencies/integration: re-exported from `lib.rs`, used by `loader.rs` and `cryfs-cli` tests.

Risks/test signals: correctness depends on the `cryfs-version` crate and root version assertion. No direct tests needed beyond version display/config update tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-config/src/version.rs -->
