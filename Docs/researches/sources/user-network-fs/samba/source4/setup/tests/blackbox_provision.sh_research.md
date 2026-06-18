# Research: sources/user-network-fs/samba/source4/setup/tests/blackbox_provision.sh

Purpose: blackbox coverage for `samba-tool domain provision` variants and base schema selection.

Control flow: it verifies provisioning over existing empty/whitespace `smb.conf`, explicit GUID/SID provisioning, DC provisions with base schemas 2008_R2 through 2019, member and standalone roles, blank DC provisioning, and reprovision of an existing target. `check_baseschema()` uses `ldbsearch` on each `sam.ldb` to verify schema `objectVersion` constants.

State and dependencies: it creates many target directories under the supplied prefix and removes them at the end. It depends on build or system `ldbsearch`, `$PYTHON`, `$BINDIR/samba-tool`, and stable schema version numbers.

Risks and test signals: failures may leave large provision directories if interrupted. Schema validation is a strong signal because it inspects the resulting database rather than just command status.
