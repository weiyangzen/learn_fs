# sources/user-network-fs/libsmb2/include/apple/config.h

## Purpose
This `config.h` snapshot configures libsmb2 for Apple platforms.

## Important APIs, Types, and Functions
It enables common POSIX headers, `HAVE_GSSAPI_GSSAPI_H`, linger, poll, sockaddr length/storage, and many system headers. `HAVE_LIBKRB5` remains undefined even though GSSAPI headers are present.

## Control Flow
Compilation uses these macros to include Apple socket, poll, GSSAPI, and platform byte-order paths. No runtime code lives here.

## State and Persistence Behavior
No runtime persistence. The header fixes feature detection for Apple builds and package strings report `libsmb2 4.0.0`.

## Dependencies and Integration Points
It integrates with Apple-specific GSS imports in `libsmb2-private.h`, Apple byte swapping in `portable-endian.h`, and the AES wrapper selecting `aes_apple.h` from `aes.c`.

## Risks and Edge Cases
GSSAPI headers are enabled but `HAVE_LIBKRB5` is not, so Kerberos code guarded by `HAVE_LIBKRB5` may be absent. Static generated macros can go stale across macOS SDK versions.

## Test Signals
Build on macOS with and without Kerberos library detection, run signed/encrypted SMB sessions, and confirm Apple AES and endian branches compile.
