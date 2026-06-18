# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/utssys.h

## Role

Defines command numbers, flags, and result structures for the legacy `utssys()` syscall family.

## Key Interfaces

- Defines `UTS_UNAME`, `UTS_USTAT`, and `UTS_FUSERS` command codes.
- Defines `UTS_FUSERS` flags for file-only, contained, NBMAND-only, device-info, and kernel-info count modes.
- `f_user_t` reports either process user info (`pid`, `uid`) or kernel device consumer info (`modid`, `instance`, `minor`) with flags.
- `fu_data_t` is a variable-length result container with max/count and first `f_user_t`.
- Defines convenience aliases for union fields and `fu_data_size(x)`.
- Defines `fu_flags` values for cwd, root, text, mapped file, open file, trace, tty, NBMAND lock, and kernel consumer.

## Risk Notes

Variable-length sizing and user/kernel union interpretation must match syscall producer and consumer logic. Flag values are ABI visible to `fuser`-style tooling.
