# sources/user-network-fs/nfs-ganesha/src/scripts/docker/entrypoint.sh-in.cmake

## Purpose
This templated Bash entrypoint starts either `/bin/bash` for `shell` mode or `ganesha.nfsd` in the foreground inside the container.

## Important APIs, Types, And Functions
The runtime API is the first command argument plus environment variables `GANESHA_LOGFILE`, `GANESHA_CONFFILE`, `GANESHA_OPTIONS`, `GANESHA_EPOCH`, and `GANESHA_LIBPATH`. The sole function, `rpc_init`, starts `rpcbind`, `rpc.statd -L`, and `rpc.idmapd`.

## Control Flow
The script assigns defaults with shell parameter expansion. If `$1` is `shell`, it runs `/bin/bash`; otherwise it runs `rpc_init` and launches `@CMAKE_INSTALL_PREFIX@/bin/ganesha.nfsd -F -L ... -f ...` with `LD_LIBRARY_PATH` set.

## State And Persistence
It starts RPC services in the container namespace and runs Ganesha in the foreground. Logs go to `GANESHA_LOGFILE`. There is no PID-file, trap, or cleanup logic.

## Dependencies And Integration Points
It depends on Bash, RPC/NFS helper binaries, the generated Ganesha install tree, and CMake substitutions for state/config/lib/install paths. It is the runtime companion to the Dockerfile template.

## Risks And Edge Cases
Unquoted environment expansion intentionally allows multi-word options but is unsafe for paths with spaces or shell metacharacters. `rpc_init` does not check failures. The daemon is not launched with `exec`, which can weaken PID 1 signal behavior. Empty `GANESHA_EPOCH` is harmless; multi-word values are split.

## Test Signals
Check generated output for no remaining `@...@` tokens. Run container `shell` mode and daemon mode with a minimal config. Test overrides for logfile, config file, options, epoch, and library path.
