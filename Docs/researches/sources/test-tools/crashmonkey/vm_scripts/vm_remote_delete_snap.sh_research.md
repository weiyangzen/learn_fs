# sources/test-tools/crashmonkey/vm_scripts/vm_remote_delete_snap.sh

Purpose: deletes CrashMonkey snapshot artifacts from a remote VM build directory using sudo.

Important APIs/types/functions: `echo password | sudo -S rm -r /home/user/projects/crashmonkey/build/snap_*` and `build/create_snap`. Control flow is two deletion commands.

State/persistence behavior: removes potentially large snapshot files/directories. Dependencies/integration: remote disk-space cleanup helper.

Risks/test signals: hard-coded password/path, destructive glob, no existence checks, and no protection against concurrent runs using snapshots.
