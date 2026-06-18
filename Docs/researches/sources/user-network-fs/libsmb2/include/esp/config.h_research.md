# sources/user-network-fs/libsmb2/include/esp/config.h

## Purpose
This generated-style `config.h` snapshot configures libsmb2 for ESP-IDF/ESP platforms.

## Important APIs, Types, and Functions
It enables many libc headers plus `HAVE_LINGER`, `HAVE_SOCKADDR_STORAGE`, `HAVE_SYS_POLL_H`, and basic POSIX socket/stat/uio support. It disables GSSAPI, Kerberos, `HAVE_NETINET_TCP_H`, sockaddr `sa_len`, `sys/time.h`, and some Unix-specific header paths.

## Control Flow
No code executes here. Conditional compilation uses these feature macros in socket, auth, and portability layers.

## State and Persistence Behavior
The header has no runtime state. It determines compiled-in transport/auth behavior for ESP builds.

## Dependencies and Integration Points
It pairs with `idf_component.yml` and the `ESP_PLATFORM` branch in `lib/CMakeLists.txt`. Kerberos is excluded, so authentication depends on NTLMSSP and local credential configuration.

## Risks and Edge Cases
ESP lwIP/socket behavior differs from POSIX despite some POSIX macros being enabled. Generated package version macros say `4.0.0`, while ESP component metadata says `3.0.1`.

## Test Signals
Build under ESP-IDF 4.2+ and run socket connection, DNS, timeout, signing, and NTLM authentication tests on device or emulator.
