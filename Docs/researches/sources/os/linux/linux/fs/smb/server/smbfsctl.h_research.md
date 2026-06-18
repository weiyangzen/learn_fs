# File Research: sources/os/linux/linux/fs/smb/server/smbfsctl.h

Defines SMB/CIFS/SMB2 FSCTL and reparse-tag numeric constants used by ioctl handling.

Key contents:
- DFS, oplock, volume, compression, sparse, object ID, reparse point, copychunk, pipe, resume key, network interface, and negotiate-validation FSCTL codes.
- Reparse tags for mount points, HSM, SIS, and WSL/Linux special files: symlink, AF_UNIX socket, FIFO, character device, and block device.
- Many constants include comments noting missing local struct definitions or future remote-use evaluation.

Role in subsystem:
- Wire-level constant registry for SMB2 ioctl/FSCTL dispatch. It contains no behavior.
