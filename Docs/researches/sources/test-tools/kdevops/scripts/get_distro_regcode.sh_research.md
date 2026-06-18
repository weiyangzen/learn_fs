<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/get_distro_regcode.sh -->
# sources/test-tools/kdevops/scripts/get_distro_regcode.sh

Purpose: dispatches to a distro-specific regulatory-code helper and prints `Unset` when no helper exists.

Important APIs and functions: no functions. It builds `DISTRO_REGCODE_SCRIPT="${TOPDIR}/scripts/get_distro_regcode_$1.sh"`, tests it with `-s`, executes it, or echoes `Unset`.

Control flow: one conditional dispatch based on whether the helper file exists and is non-empty.

State and persistence: read-only; output depends on `${TOPDIR}` and the first positional argument.

Dependencies and integration: bash and distro-specific sibling scripts. It likely feeds wireless/regulatory Kconfig defaults.

Risks: `$1` and `$TOPDIR` are not validated. The target helper is executed without quoting, so spaces in `TOPDIR` fail. Since `$1` is embedded in a path, callers must keep it to trusted distro identifiers. Test signals include helper-present/helper-missing cases, empty helper file, missing TOPDIR, and arguments with unexpected characters.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/get_distro_regcode.sh -->
