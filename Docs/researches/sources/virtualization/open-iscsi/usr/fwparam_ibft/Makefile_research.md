# File Research: sources/virtualization/open-iscsi/usr/fwparam_ibft/Makefile

Builds firmware boot parameter helper objects for iBFT/OpenFirmware support. Objects include `fw_entry.o`, `fwparam_sysfs.o`, generated parser/lexer objects, and `fwparam_ppc.o`.

Important details:
- Adds PIC, warning flags, open-iscsi include paths, and version/SBINDIR defines.
- Lex/bison generated C files are checked in; rules only regenerate them when missing.
- `depend` generates `.depend` from C sources.
- `clean` removes objects, parser output files, and `.depend`.
