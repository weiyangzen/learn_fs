# File Research: sources/virtualization/guestfs-tools/tail/test-virt-tail.sh

Functional integration test for `virt-tail`.

Key behavior:
- Requires direct backend because libvirt can alter SELinux labels and prevent continued `guestfish` writes to the test disk.
- Starts a listening `guestfish` session.
- Creates a 10M disk, partitions it, formats ext2, mounts it, and writes `/tail` with `line 1`.
- Runs `virt-tail -a $disk -m /dev/sda1 /tail` in the background and captures output.
- Waits up to 10 minutes for initial output.
- Appends `line 2` and `line 3`, syncs, and waits for continued output.
- Deletes `/tail`, syncs, waits for `virt-tail`, and expects zero exit.
- Trap cleanup shuts down guestfish, kills background process if needed, and removes files on success.

Research notes:
- Tests initial tail output, follow behavior, and graceful exit when watched file is deleted.
