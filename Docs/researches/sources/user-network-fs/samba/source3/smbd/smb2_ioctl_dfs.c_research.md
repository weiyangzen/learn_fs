# sources/user-network-fs/samba/source3/smbd/smb2_ioctl_dfs.c

Purpose: handles DFS FSCTLs, especially `FSCTL_DFS_GET_REFERRALS`, and falls back to VFS FSCTL for other DFS-device controls.

Important APIs: `smb2_ioctl_dfs()` is the module dispatcher. `fsctl_dfs_get_refers()` decodes referral level and path, generates referral data, and packages output.

Control flow: `FSCTL_DFS_GET_REFERRALS` requires host msdfs enabled and at least four input bytes. It reads the max referral level, converts the remaining UTF-16 path to Unix charset, calls `setup_dfs_referral()`, truncates output to `in_max_output` with `STATUS_BUFFER_OVERFLOW` when needed, and otherwise returns OK. Unknown DFS control codes call `SMB_VFS_FSCTL()` if an fsp exists and translate `NOT_SUPPORTED` to `FS_DRIVER_REQUIRED` on IPC or `INVALID_DEVICE_REQUEST` elsewhere.

State and persistence: read-only except transient output allocation. It reads DFS configuration and referral metadata.

Dependencies and integration: depends on loadparm DFS settings, string conversion, `setup_dfs_referral()`, VFS FSCTL fallback, and shared IOCTL state.

Risks: referral truncation is noted in source as needing tests. Disabled host DFS, invalid UTF-16, and unsupported fallback all need distinct statuses. Ownership moves from `setup_dfs_referral()` allocated memory into a talloc data blob.

Test signals: cover SMB2 DFS path suites, non-DFS share behavior, leading backslash DFS cases, malformed short input, invalid UTF-16, host DFS disabled, referral output overflow, and unsupported DFS control fallback.
