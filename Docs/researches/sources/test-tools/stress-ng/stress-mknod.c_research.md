# sources/test-tools/stress-ng/stress-mknod.c

Purpose: `stress-mknod.c` exercises `mknod` and, when available, `mknodat` by creating and deleting many temporary node paths plus optional character/block special devices based on real `/dev` device numbers.

Important APIs/types/functions: `stress_mknod_modes_t` defines supported file node mode rows for FIFO, regular file, named socket, and directory when macros are present. `stress_mknod_tidy` removes gray-code-named temp paths. `stress_mknod_find_dev` scans `/dev` for the first matching char/block device and copies `st_rdev`. `stress_mknod_check_errno` treats resource/permission/read-only/invalid errors as benign for stress purposes. `stress_do_mknod` randomly chooses `mknodat` or `mknod` and also probes a known bad fd path.

Control flow: `stress_mknod` validates that at least one mode exists, finds char and block device numbers if possible, creates a temp dir, optionally opens it as an `O_DIRECTORY` fd for `mknodat`, synchronizes, then loops. Each loop tries special char/block node creation if real devices were found, then creates up to `DEFAULT_DIRS` temp nodes with gray-code filenames and random modes, increments bogo operations on successful creation, tidies created paths, syncs, and repeats.

State and persistence behavior: filesystem state is temporary under the stress-ng temp directory. The stressor force-unlinks paths before and after operations and removes the temp directory on exit. It holds only a directory fd and local device ids; no persistent state is intended.

Dependencies and integration points: the file uses Linux-only `mknod`, optional `mknodat`, `basename`, stress-ng temp-file helpers, bad-fd helper, force unlink wrappers, and sync wrapper. It registers `stress_mknod_info` as `CLASS_FILESYSTEM | CLASS_OS` with `VERIFY_ALWAYS`; unsupported builds register “only supported on Linux”.

Risks: permissions, capabilities, filesystem type, quotas, and read-only mounts strongly influence expected errors, so the ignored errno set is necessary. Creating special devices is sensitive and should only use copied device ids, not random ids. Cleanup must remain robust because some mode attempts, especially directories or sockets, may require different removal semantics; current cleanup uses unlink and force unlink paths.

Test signals: run `stress-ng --mknod 1 --mknod-ops 1 --verify` as an unprivileged user and, separately, on filesystems with limited mknod support. Confirm benign errors do not fail the stressor, unexpected errno is reported, and no temp paths remain.
