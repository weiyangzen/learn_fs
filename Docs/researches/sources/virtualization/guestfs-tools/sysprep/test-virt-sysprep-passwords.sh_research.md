# File Research: sources/virtualization/guestfs-tools/sysprep/test-virt-sysprep-passwords.sh

Test for password customization combinations in `virt-sysprep`.

Key behavior:
- Requires phony Fedora image.
- Creates a qcow2 overlay and appends eleven test users to `/etc/shadow`.
- Writes a local `password` file containing `123456`.
- Runs `virt-sysprep --enable customize` with password specifications covering direct passwords, salted passwords, file input, random, disabled, locked password, locked salted password, locked file, locked random, locked disabled, and locked-only.
- Cleans overlay and password file.

Research notes:
- The script validates that all accepted password option forms parse and execute without failure; it does not inspect resulting hashes in this file.
