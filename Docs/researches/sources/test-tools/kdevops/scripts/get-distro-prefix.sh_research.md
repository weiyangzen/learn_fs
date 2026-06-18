<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/get-distro-prefix.sh -->
# sources/test-tools/kdevops/scripts/get-distro-prefix.sh

Purpose: should detect a distro prefix from a fixed list and fall back to `debian`.

Important APIs and functions: no functions. It defines `DEFAULT_DISTRO=debian`, iterates distro names, and is intended to call `./scripts/os-release-check.sh`.

Control flow: as written, the `if` compares the literal string `"./scripts/os-release-check.sh $i"` to `"y"` rather than executing the command. That condition is always false, so the script always echoes `debian`.

State and persistence: read-only; no writes.

Dependencies and integration: bash. `scripts/provision.Makefile` exports `KDEVOPS_DEFAULT_DISTRO` from this script.

Risks: the current command-substitution bug means non-Debian hosts are misdetected, which can cascade into default provisioning and Kconfig choices. The script also assumes repo-root execution if fixed to use the relative helper. Test signals should include distro-detection fixtures or a stub `os-release-check.sh`; current behavior can be captured by asserting it returns `debian` even when the stub would return `y` for Fedora.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/get-distro-prefix.sh -->
