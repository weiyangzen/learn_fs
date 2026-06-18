# File Research: sources/virtualization/guestfs-tools/df/test-virt-df.sh

## Scope

Direct-image regression test for `virt-df`.

## Behavior

- Runs `virt-df --format=raw -a fedora.img`.
- Verifies the output starts with a title line.
- Verifies exactly six lines: header plus five filesystems.
- Checks that `/dev/VG/LV1`, `/dev/VG/LV2`, `/dev/VG/LV3`, `/dev/VG/Root`, and `/dev/[hsv]da1` appear.
- Contains disabled detailed numeric comparisons documenting expected `df`/`df -h`/`df -i` values.

## Dependencies And Risks

- Depends on the phony Fedora filesystem layout.
- Detailed space accounting is intentionally disabled due historical mismatch concerns.
