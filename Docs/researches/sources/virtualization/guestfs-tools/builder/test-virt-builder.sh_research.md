# File Research: sources/virtualization/guestfs-tools/builder/test-virt-builder.sh

## Scope

Core virt-builder customization integration test using a phony Fedora template.

## Behavior

- Requires `fedora.xz` in the build directory.
- Builds `phony-fedora` into qcow2 output with size, format, arch, hostname, timezone, root password, directory creation, writes, uploads, edits, deletes, symlinks, appended lines, ownership change, firstboot script, and firstboot package list.
- Uses `guestfish` to verify resulting guest content and metadata.
- Compares full expected output, including hostname, timezone symlink, shadow hash prefix, appended file contents, symlinks, and uid/gid.

## Dependencies And Risks

- Avoids `$VG` for the main `virt-builder` invocation because libtool has trouble with multiline parameters.
- Strongly asserts behavior of common customize operations.
- Uses a phony guest, so package install/run-command behavior is intentionally not covered.
