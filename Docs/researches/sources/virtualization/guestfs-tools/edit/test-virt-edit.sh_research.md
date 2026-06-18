# File Research: sources/virtualization/guestfs-tools/edit/test-virt-edit.sh

Functional shell test for `virt-edit`. It creates a writable qcow2 overlay backed by the Fedora phony guest image, edits `/etc/test3`, and validates content and metadata.

Coverage:
- Creates `test.qcow2` with `guestfish disk-create`, backing `../test-data/phony-guests/fedora.img`.
- Simulates interactive editing by setting `EDITOR='echo newline >>'`.
- Verifies `virt-cat` output includes the appended line.
- If Perl exists, tests noninteractive `-e 's/^[a-f]/$lineno/'`.
- Verifies edited file mode, UID, and GID remain `0600`, `10`, and `11`, guarding RHBZ#788641 behavior.
- Removes the temporary image.

Research relevance: confirms content mutation and metadata preservation for in-guest file edits.
