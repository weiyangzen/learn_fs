# sources/test-tools/kdevops/scripts/version_check/ansible-playbook

## Purpose
Checks that the installed `ansible-playbook` version meets kdevops' minimum requirement.

## Important APIs and control flow
The script sets `MIN_REQ=2.13.4`, derives `OWN_VER` from `ansible-playbook --version`, normalizes both versions through `${TOPDIR}/scripts/ld-version.sh`, and compares the normalized integers. If installed version is older it prints `ansible-playbook >= 2.13.4 required` and exits 1.

## State and dependencies
Read-only. Depends on `ansible-playbook`, `head`, `awk`, `sed`, and `TOPDIR/scripts/ld-version.sh`.

## Integration points
Used as a version gate before running Ansible-based workflows.

## Risks and test signals
If `TOPDIR` is unset or `ansible-playbook` is missing, errors will come from shell command substitution rather than a tailored diagnostic. Version parsing assumes the version is the last token of the first output line after removing `]`. Test with supported, unsupported, and missing Ansible installs.
