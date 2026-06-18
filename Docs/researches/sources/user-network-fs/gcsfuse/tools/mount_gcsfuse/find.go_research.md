# sources/user-network-fs/gcsfuse/tools/mount_gcsfuse/find.go

Purpose: locates `fusermount` and `gcsfuse` executables for the mount helper.

Important APIs/types/functions: `findFusermount` and `findGcsfuse`.

Control flow: `findFusermount` returns empty on non-Linux; on Linux it checks hard-coded absolute candidates. `findGcsfuse` checks `gcsfuse` via PATH first and then several absolute locations.

State/persistence behavior: no persistent state; it only probes executable availability.

Dependencies/integration: used by `mount_gcsfuse/main.go` before invoking gcsfuse. Uses `exec.LookPath` and `runtime.GOOS`.

Risks/test signals: hard-coded paths can miss distro-specific locations. On non-Linux, `findFusermount` returns nil error and empty path, which leads to an empty PATH directory in the caller.
