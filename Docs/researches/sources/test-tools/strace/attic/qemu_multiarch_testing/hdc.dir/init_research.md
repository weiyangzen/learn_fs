<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/attic/qemu_multiarch_testing/hdc.dir/init -->
# sources/test-tools/strace/attic/qemu_multiarch_testing/hdc.dir/init

Purpose: minimal init script for a QEMU test disk image that copies mounted content into `/home` and transfers control to `init2`.

Important commands: prints a status message, runs `cp -a /mnt /home` with diagnostic exit on failure, changes directory to `/home/mnt`, and `exec`s `./init2`.

Control flow: linear boot-time shell flow. If `exec ./init2` fails, a final diagnostic is printed.

State and persistence: copies the `/mnt` tree into the image's `/home`, changing filesystem contents before the build phase.

Dependencies and integration: integrated with `make-hdc-img.sh` image creation and `init2` build script. Assumes `/mnt` is mounted and contains the strace tree.

Risks: broad recursive copy can consume limited image space. Failure handling is minimal after `exec`. Test signals: boot the image and verify logs include "Copying to /home" followed by `init2` activity.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/attic/qemu_multiarch_testing/hdc.dir/init -->
