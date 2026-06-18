# Research: sources/user-network-fs/samba/source4/setup/tests/blackbox_supported_features.sh

Purpose: tests Samba database feature gating via `compatibleFeatures` and `requiredFeatures` on `@SAMBA_DSDB`.

Control flow: it provisions a DC, adds a fake compatible feature with `ldbmodify`, verifies it is not returned by `ldbsearch`, verifies a normal object can still be found, then adds a fake required feature and expects subsequent `ldbsearch` to fail.

State and dependencies: directly mutates `sam.ldb` using build or system `ldbmodify`, `ldbdel`, and `ldbsearch`. It removes the database path at the end.

Risks and test signals: direct LDB writes bypass normal tooling, which is intentional for feature-flag simulation. Expected search failure after `requiredFeatures` is the core signal.
