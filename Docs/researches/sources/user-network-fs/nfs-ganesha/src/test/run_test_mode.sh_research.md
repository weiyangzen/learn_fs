# sources/user-network-fs/nfs-ganesha/src/test/run_test_mode.sh

Purpose: launches a locally built `ganesha.nfsd` in a simple VFS export configuration suitable for presubmit protocol tests such as pynfs or cthon.

Important APIs, types, and functions: shell inputs are one `build_path`; derived paths include `ganesha.nfsd`, VFS plugin directory, temporary config/log/pid/export paths. It invokes `sudo "$GANESHA_EXE" -F -x -f ...`.

Control flow: validates argument count and executable presence, creates a temporary directory under `$HOME/ganesha-test-mode`, writes a minimal NFSv3/v4 VFS config, then runs ganesha in foreground with logging and pid file.

State and persistence: creates temporary directories and files under the user's home directory. It does not clean them up automatically because the server runs foreground and may be terminated externally.

Dependencies and integration points: depends on a completed build tree with `ganesha.nfsd` and VFS plugin, sudo privileges, VFS FSAL, and external test suites pointed at `/export`.

Risks: unquoted `mkdir --parents $EXPORT_PATH` can mis-handle spaces. It assumes plugin path layout under `FSAL/FSAL_VFS/vfs/`. Running under sudo changes permissions and environment expectations. The script uses `set -euo pipefail`, so any missing variable or command failure terminates immediately.

Test signals: useful as an integration harness rather than a unit test. Success is a running foreground server ready for external NFS test clients.
