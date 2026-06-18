# sources/user-network-fs/bazil-fuse/fuse_linux.go

Purpose: This Linux-specific file defines the maximum kernel write request size supported by the library.

Important APIs, types, and functions: It declares `const maxWrite = 128 * 1024`.

Control flow: No runtime control flow.

State and persistence behavior: No state or persistence.

Dependencies and integration points: `fuse.go` uses `maxWrite` to size the request buffer and cap `initResponse.MaxWrite`. The comment ties the value to observed Linux 4.2 behavior with 32 FUSE pages of 4 KiB each.

Risks: Kernels with larger maximum page/request configurations could support larger writes than this library advertises. Because the library advertises this cap, the kernel should not send larger writes after negotiation.

Test signals: `serve_test.go` has `TestWriteLarge`, which exercises multi-request or large-buffer write behavior through the negotiated limit.
