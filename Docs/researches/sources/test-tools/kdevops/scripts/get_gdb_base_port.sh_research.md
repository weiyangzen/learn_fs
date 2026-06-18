<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/get_gdb_base_port.sh -->
# sources/test-tools/kdevops/scripts/get_gdb_base_port.sh

Purpose: deterministically derives a base gdbserver port from the script file's MD5 checksum.

Important APIs and functions: no functions. It runs `md5sum "$0"`, strips non-digits from the checksum, takes the last four digits, and echoes them.

Control flow: linear checksum, digit filtering, substring extraction, print.

State and persistence: no writes. The output changes when this script's content/path target changes enough to alter the checksum.

Dependencies and integration: bash, md5sum, awk, tr. `kconfigs/Kconfig.libvirt` uses it as the default for `LIBVIRT` gdb base port.

Risks: last four digits can produce low, reserved, or already-used ports, and may be fewer than four digits if the checksum digit string is unexpectedly short. It does not ensure numeric range suitability. Test signals include asserting stable output for a known file copy and validating the result is numeric and acceptable for the consuming Kconfig.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/get_gdb_base_port.sh -->
