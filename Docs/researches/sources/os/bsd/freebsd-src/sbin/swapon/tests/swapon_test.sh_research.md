# File Research: sources/os/bsd/freebsd-src/sbin/swapon/tests/swapon_test.sh

## Summary
ATF shell tests for `swapon` fstab-driven md-backed swap handling, including explicit and automatic md units and GELI-encrypted variants.

## Main Elements
- Creates swapfiles at least two kernel pages for successful attach cases.
- Tests `mdN`, `/dev/mdN`, `md`, and `/dev/md` fstab forms.
- Tests `mdN.eli`, `/dev/mdN.eli`, `md.eli`, and `/dev/md.eli` encrypted forms.
- Uses alternate fstab files with `sw,file=swapfile`.
- Verifies expected `swapon` output for fixed and dynamically allocated md units.
- Cleans up each successful case with `swapoff -F fstab.out -a`.
- Tests too-small swapfile rejection and manually detaches the md unit after failure.

## Dependencies And Integration
Uses ATF shell, `sysctl hw.pagesize`, `truncate`, `swapon`, `swapoff`, and `mdconfig`. Requires root.

## Research Notes
The tests specifically cover name parsing paths added for md-backed fstab swap entries, including both `/dev/`-prefixed and unprefixed names.
