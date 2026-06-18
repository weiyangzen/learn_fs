# File Research: sources/virtualization/guestfs-tools/sysprep/test-virt-sysprep-script.sh

Test for `virt-sysprep --script` operation behavior.

Key behavior:
- Requires FUSE and phony Fedora image.
- Exports `abs_builddir` for helper scripts.
- Runs `script1.sh` and `script2.sh` together and verifies both stamp files are created.
- Runs failing `script3.sh` and verifies `virt-sysprep` exits with error.
- Runs `script4.sh` twice, verifies two stamp lines exist, and verifies the two paths differ.

Research notes:
- Covers script execution, failure propagation, and per-run temporary directory isolation.
