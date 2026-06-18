# sources/security-integrity/selinux/sandbox/seunshare.c
# sources/security-integrity/selinux/sandbox/seunshare.c

Purpose: privileged helper that creates a private mount namespace, bind-mounts alternate home/tmp/runtime dirs, sets a SELinux execution context, drops privileges/capabilities, and executes the sandboxed command.

Important APIs and control flow: helper functions drop capabilities (`cap-ng`), drop UIDs, forward SIGINT to child process groups, verify user shell, pin directories with `O_NOFOLLOW`, validate ownership, bind-mount directories/files using `/proc/self/fd`, reject bad glob paths, build rsync commands, recursively remove temp dirs without following symlinks, verify `setfsuid()` transitions, create/populate root-owned runtime tmpdirs, and clean them by rsyncing back then deleting. `main()` parses options for capabilities, kill, home/tmp/runuser, Wayland/PipeWire sockets, and context; validates socket names, source dirs, SELinux availability, and user shell; creates a runtime tmpdir; forks. The child unshares mount namespace, remounts `/` as slave, re-pins and re-validates dirs in the child namespace, bind-mounts runtime sockets and directories, clears/reconstructs the environment, changes home, sets SELinux context via `setcon()` or `setexeccon()`, and execs. The parent drops caps, waits, terminates the child process group, warns about deprecated kill behavior, and cleans tmpdir.

State and persistence: creates `/tmp/.sandbox-USER-XXXXXX`, copies tmp contents in/out with rsync, mutates child mount namespace, and may bind runtime socket files. Persistent changes come from copied-back tmpdir content.

Dependencies and integration points: setuid-installed by sandbox Makefile, invoked by Python `sandbox`, depends on libselinux, libcap-ng, rsync, mount namespace support, `/etc/shells`, and Linux-specific fsuid/mount APIs.

Risks and test signals: this is high-risk setuid code. It mitigates symlink/race attacks with `O_NOFOLLOW`, inode rechecks, fsuid changes, and fd-based mounts, but any gap is security-sensitive. Capabilities option appears to leave capability selection at `CAPNG_SELECT_CAPS`, while default also initializes that value, so intended capability behavior should be audited. Sandbox tests exercise mount/homedir/tmpdir paths but not race resistance, socket bind mounts, or graphical runtime behavior.
