# sources/user-network-fs/libfuse/include/fuse_service.h

`fuse_service.h` is the public API for libfuse servers launched under a mount service helper, gated behind `FUSE_USE_VERSION >= 3.19`. It lets a filesystem accept service-provided arguments, request privileged file opens, and ask the service to perform the mount.

The opaque type is `struct fuse_service`. Functions include `fuse_service_accept`, `fuse_service_accepted`, capability checks for `allow_other` and `fuseblk`, release/destroy, argument append and effective command-line construction, service-specific command-line parsing, file/block-device request and receive calls, finish-file-requests, mount-format expectation, `fuse_service_session_mount`, goodbye, and service exit. `FUSE_SERVICE_REQUEST_FILE_QUIET` marks optional file requests.

Typical flow is accept service context, append helper args to `fuse_args`, parse options without local mountpoint checks, request any helper-opened descriptors, create a FUSE session, and call `fuse_service_session_mount` instead of normal mount/daemonization. State is the service socket/context, negotiated helper capabilities, expected mount format, and requested file lifecycle.

Risks include version-gating surprises, incorrectly calling `fuse_daemonize` in service mode, trusting helper-provided descriptors/options without validating policy, and mount format or `allow_other`/`fuseblk` capability drift. Test signals include no-service fallback, accept/append, capability checks, command-line ownership, file/block-device request flows, quiet failures, finish ordering, mount format validation, service mount, goodbye/exit status, and compile gating.
