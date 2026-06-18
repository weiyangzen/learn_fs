# File Research: sources/os/bsd/freebsd-src/sbin/mdconfig/tests/mdconfig_test.sh

## Summary
ATF shell tests for `mdconfig` attach, resize, listing, and verbose query behavior.

## Main Elements
- `check_diskinfo()` validates sector size, media size, sector count, stripe size, and offset using `diskinfo`.
- `cleanup_common()` detaches the md device recorded in `mdconfig.out`.
- Tests implicit and explicit vnode attach modes.
- Tests vnode sizes smaller and larger than backing file size.
- Tests non-default sector size.
- Tests `malloc` and `swap` md types.
- Tests attaching a specific unit number.
- Tests provider size round-down to sector-size multiples on attach and resize.
- Tests verbose listing with options such as `force,reserve`.

## Dependencies And Integration
Requires `mdconfig`, `diskinfo`, `truncate`, shell, and root privileges. Exercises the live md(4)/GEOM stack.

## Research Notes
The tests intentionally inspect both kernel-visible device geometry and `mdconfig -lv` user-facing output, catching regressions in ioctl behavior and formatting.
