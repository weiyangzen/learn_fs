# sources/user-network-fs/bazil-fuse/fuse_freebsd.go

Purpose: This FreeBSD-specific file defines the maximum write payload size the library is prepared to receive from the kernel.

Important APIs, types, and functions: It declares `const maxWrite = 128 * 1024`, used by `fuse.go` to size request buffers and advertise `MaxWrite` during init negotiation.

Control flow: There is no runtime control flow in this file. The build tag is implicit by filename suffix; Go includes it for FreeBSD builds.

State and persistence behavior: No state or persistence.

Dependencies and integration points: `maxWrite` feeds `bufSize` and `initResponse.MaxWrite` in `fuse.go`.

Risks: The comment says the value is a guess on FreeBSD. If the kernel sends larger writes than this buffer supports, the library can reject or fail large write handling.

Test signals: Large write behavior is exercised by `serve_test.go` through `TestWriteLarge`, but no FreeBSD-only unit directly validates this constant.
