# File Research: sources/virtualization/guestfs-tools/win-reg/Makefile.am

Automake file for the Perl script `virt-win-reg`.

Key behavior:
- Includes shared `subdir-rules.mk`.
- Installs `virt-win-reg` as `bin_SCRIPTS`.
- Generates `virt-win-reg.1` and website HTML through `PODWRAPPER`.
- Uses `--license GPLv2+` and `--warning custom` because the script’s POD includes its own registry modification warning.

Research notes:
- There are no tests listed in this Makefile.
