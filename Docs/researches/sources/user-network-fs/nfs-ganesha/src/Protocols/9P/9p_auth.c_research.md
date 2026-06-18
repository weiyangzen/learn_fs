## sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_auth.c

Purpose: handles `TAUTH` parsing for 9P but deliberately does not implement authentication fids.

APIs and flow: `_9p_auth` decodes tag, afid, uname, aname, and numeric user field, logs the request, validates that `afid` is within `_9P_FID_PER_CONN`, then returns `EOPNOTSUPP` via `_9p_rerror`.

State/dependencies: it does not create fid state or touch FSAL. It depends only on 9P wire helpers and the common error response path.

Risks/tests: clients must be prepared to continue with unauthenticated `TATTACH` credential handling. Test signals are correct `ERANGE` for out-of-range afid and `EOPNOTSUPP` for otherwise valid requests.
