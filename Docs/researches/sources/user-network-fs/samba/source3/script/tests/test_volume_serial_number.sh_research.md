# sources/user-network-fs/samba/source3/script/tests/test_volume_serial_number.sh

Purpose: verifies that the per-share `volume serial number` parameter is exposed through smbclient's `volume` command.

Important functions and APIs: uses `smbclient` and `subunit.sh`. `test_serial_number()` runs `smbclient //SERVER_IP/SHARENAME -U USERNAME%PASSWORD -c volume`, echoes the output, and greps for `0xdeadbeef`.

Control flow: argument parsing is followed by a single subunit-wrapped check. Any smbclient failure or missing expected serial string fails the test.

State and persistence: no local or server-side mutation.

Dependencies and integration: registered in `selftest/tests.py` as `samba3.blackbox.volumeserialnumber`, targeting the `volumeserialnumber` share in the `fileserver` environment. It depends on smb.conf setting the expected serial value.

Risks and test signals: string matching is simple and case-sensitive; output-format changes can require updates. Passing signal is the expected hexadecimal serial value in `volume` output.
