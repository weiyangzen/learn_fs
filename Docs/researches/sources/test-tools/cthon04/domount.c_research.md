# sources/test-tools/cthon04/domount.c

Purpose: tiny setuid-oriented wrapper that execs the platform mount or umount command for the Connectathon test harness.

Important APIs/types/functions: main() inspects argv[1] for -u, getenv("UMOUNT")/getenv("MOUNT"), setuid(0), execv(), and exit(). It mutates argv in place so execv receives the selected command path as argv[0] while preserving remaining arguments.

Control flow: if -u is present, the command becomes UMOUNT or /etc/umount and argv is advanced past the wrapper name; otherwise the command becomes MOUNT or /etc/mount. The process sets effective uid to root, execs the selected command, and exits 1 only if execv fails.

State and persistence behavior: does not persist data itself, but when installed setuid root it can mount or unmount filesystems and therefore changes system mount state.

Dependencies and integration points: used by harness scripts that need privileged mount/umount without embedding platform paths. It expects traditional /etc/mount and /etc/umount defaults unless overridden by environment.

Risks: setuid root plus environment-selected executable path is a major security risk outside a controlled test lab; missing string/unistd headers produce old-C implicit declarations; no diagnostics are emitted on exec failure.

Test signals: success is replacement by the mount/umount program. A direct exit status 1 means command exec failed.
