# File Research: sources/os/linux/linux/fs/smb/server/mgmt/user_config.h

This header defines `struct ksmbd_user` and accessors for user state.

Fields include:
- User flags.
- uid/gid.
- Account name.
- Passkey/hash and size.
- Supplementary group count and gid array.

Inline helpers test/set flags, detect guest flag, and return name/passkey/uid/gid. Public APIs cover login, allocation, free, anonymous check, and user comparison.

`set_user_guest()` is currently an empty inline, so guest status is represented by flags populated elsewhere rather than by this helper.
