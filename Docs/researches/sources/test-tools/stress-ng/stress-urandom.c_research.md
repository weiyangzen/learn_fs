## sources/test-tools/stress-ng/stress-urandom.c

Purpose: Implements `urandom`, stressing `/dev/urandom`, nonblocking/blocking `/dev/random`, random ioctls, select readiness, mmap attempts, and optional verification of permission failures.

Important APIs/types/functions: `stress_urandom_info`, `stress_urandom`, and `check_eperm`; uses random device fds, `read`, `ioctl(RNDGETENTCNT/RNDCLEARPOOL/RNDZAPENTCNT/RNDADDTOENTCNT/RNDRESEEDCRNG)`, `select`, `mmap`, `mprotect`, and optional writes to `/dev/random`.

Control flow: opens available random devices, synchronizes, reads large chunks from `/dev/urandom`, conditionally reads one byte from `/dev/random` only when entropy is high enough, probes privileged ioctls only when not `CAP_SYS_ADMIN`, mmaps `/dev/urandom`, and uses `select` before potentially blocking random reads.

State and persistence: only device descriptors and metrics; it avoids destructive entropy operations when privileged.

Dependencies/integration: Linux random ioctls, capability helper, page-size handling, and stress-ng metrics.

Risks: device absence yields not-implemented skip; entropy depletion is avoided but still environment-sensitive; optional verification assumes privileged ioctls fail with expected errno.

Test signals: optional verify checks EPERM-like failures; metrics report random bits read and bits/sec.
