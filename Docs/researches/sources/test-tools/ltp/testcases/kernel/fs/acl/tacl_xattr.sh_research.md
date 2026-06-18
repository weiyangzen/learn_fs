# sources/test-tools/ltp/testcases/kernel/fs/acl/tacl_xattr.sh

Purpose: legacy root-only shell test for POSIX ACL and extended attribute behavior on a loopback ext2/ext3 filesystem mounted with `acl,user_xattr`.

Important APIs/types/functions: shell commands `dd`, `losetup`, `mkfs`, `mount`, `useradd`, `userdel`, `su`, `setfacl`, `getfacl`, `chmod`, `chown`, `attr`, `getfattr`, `setfattr`, `diff`, `umount`, and filesystem paths under `tacl/`.

Control flow: the script requires UID 0, creates `tacl/blkext2`, attaches `/dev/loop0`, formats ext2 or ext3 depending on existing mount output, mounts it, creates four local users, and builds directories/files/symlinks owned by test users. ACL tests then manipulate owner, named user, group, mask, other, default ACL, chmod/chown, and backup/restore semantics, checking success by file creation, `ls -l`, `getfacl`, and `diff`. Xattr tests attach attributes to directories/files/symlinks, dump logical/physical traversals, get/remove attributes, backup/restore with hex encoding, then delete users, unmount, and remove `tacl`.

State/persistence behavior: destructive and persistent until cleanup. It creates system users, modifies a fixed `/dev/loop0`, formats a loopback block file, mounts a filesystem, writes ACL/xattr data, and removes everything at the end.

Dependencies/integration: depends on root, loop device support, mkfs/mount ACL/xattr support, `acl` and `attr` userland tools, local user management, and a test environment where `/dev/loop0` is safe.

Risks/test signals: high operational risk because fixed user names and `/dev/loop0` can collide with host state, and many checks print `FAILED` without exiting nonzero immediately. Some filename typos (`newfil` vs `newfile`) weaken assertions. Test signal is textual success/failure plus final cleanup completing.
