# File Research: sources/virtualization/guestfs-tools/resize/test-virt-resize.pl

Stochastic Perl test generator for `virt-resize`.

Key behavior:
- Uses `Sys::Guestfs` to synthesize randomized source disks and then runs `virt-resize`.
- Skips if `SKIP_TEST_VIRT_RESIZE_PL` is set, Perl is older than 5.14, or the host is 32-bit.
- Accepts `--seed=SEED` for reproducible randomized failures; prints seed and chosen parameters before disk creation.
- Randomizes MBR/GPT, partition count, expand versus shrink, raw/qcow2 input and output formats, filesystem type, and extra-partition behavior.
- Avoids known-broken MBR extended/logical shrink cases by limiting some MBR tests to three partitions.
- Filesystem matrix includes ext2, LVM, NTFS when available, btrfs when available, and XFS only for expand.
- Creates partitions, filesystems, optional LVM, and pre-shrunk filesystems/PVs for shrink cases.
- Computes a target disk size from requested partition transformations.
- Constructs `virt-resize --debug --format ... --output-format ...` with `--resize`, `--expand`, `--shrink`, optional `--lvexpand`, `--ntfsresize-force`, and `--no-extra-partition`.
- Deletes source and target images after success.

Research notes:
- The test’s value is broad randomized coverage of partition/filesystem transformations, with reproducible failure seeds.
