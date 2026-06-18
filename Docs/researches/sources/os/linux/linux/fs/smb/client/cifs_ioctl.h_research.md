# File Research: sources/os/linux/linux/fs/smb/client/cifs_ioctl.h

Userspace ioctl ABI structures and command numbers for CIFS/SMB3.

It defines packed mount/share info structs, snapshot enumeration header, passthrough query/fsctl/set-info request header, key-dump debug structures, and notify request/response structures.

Ioctls include copychunk, set integrity, get mount info, enumerate snapshots, query info, dump session/encryption keys, notify, full key dump, get tcon info, and shutdown. The file also defines shutdown mode flags for going-down behavior.

Security-sensitive note: key-dump structs expose encryption/session material and are intended for debug paths guarded elsewhere by config and ioctl handling.
