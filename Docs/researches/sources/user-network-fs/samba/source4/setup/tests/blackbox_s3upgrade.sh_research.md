# Research: sources/user-network-fs/samba/source4/setup/tests/blackbox_s3upgrade.sh

Purpose: blackbox tests for classic Samba 3 to Samba 4 upgrade paths.

Control flow: it copies `testdata/samba3`, writes three temporary Samba 3 configs, runs `samba-tool domain classicupgrade` for member and DC-like configurations, tests upgrade with `--testparm`, and verifies local/domain SIDs using `net getlocalsid` and `net getdomainsid`. It exercises both dbdir-driven and testparm-driven discovery.

State and dependencies: it writes temporary `smb*.conf` files and upgraded S4 target directories under `$PREFIX/samba3-upgrade`, then removes them. Dependencies include `samba-tool`, `net`, `testparm`, testdata, and passdb/WINS files.

Risks and test signals: it uses generated configs with paths embedded from `$PREFIX`, so whitespace in paths can be risky. SID checks are strong signals that upgrade preserved domain identity.
