# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zut/zut.conf

This is the driver configuration file for the ZFS unit-test pseudo device. Its only active configuration line is:

`name="zut" parent="pseudo";`

That binds the `zut` driver to the pseudo nexus so the module can attach as a pseudo-device and create `/dev/zut`. The rest of the file is the CDDL/license and copyright header.
