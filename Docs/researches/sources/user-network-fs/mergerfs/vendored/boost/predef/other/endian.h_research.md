# sources/user-network-fs/mergerfs/vendored/boost/predef/other/endian.h

Purpose: Conservatively detects byte and word endianness for Boost.Predef. It exposes four mutually searched categories: big-byte, big-word, little-byte, and little-word.

Important APIs, types, and functions: Defines `BOOST_ENDIAN_BIG_BYTE`, `BOOST_ENDIAN_BIG_WORD`, `BOOST_ENDIAN_LITTLE_BYTE`, `BOOST_ENDIAN_LITTLE_WORD`, corresponding `*_AVAILABLE` macros, and name macros. Public behavior is macro-only.

Control flow: All endian macros begin as not available. The detector first tries system headers (`endian.h`, `machine/endian.h`, or `sys/endian.h`) for GNU libc, Android, OpenBSD, macOS, and BSD targets. It then checks `__BYTE_ORDER` or `_BYTE_ORDER`. If still unknown, it checks compiler/architecture markers such as ARM/MIPS endian variants, LoongArch, RISC-V, and E2K. It finally falls back to known fixed-endian Boost architecture macros and treats Windows on ARM as little-endian.

State and persistence behavior: Compile-time-only. It stops further detection once any endian category is set, so earlier reliable OS headers take precedence over generic architecture assumptions.

Dependencies and integration points: Depends on Boost.Predef C library, OS, platform, and architecture detectors. Hash-table code in this vendored Boost tree indirectly benefits from correct endian and architecture detection through `boost/predef.h`.

Risks: It explicitly avoids reporting bi-endianness. Cross-compilers or unusual libc header combinations may leave all endian macros unavailable or choose the OS-header result over architecture defaults. A minor naming oddity exists in `BOOST_ENDIAN_BIG_WORD_BYTE_AVAILABLE` and `BOOST_ENDIAN_LITTLE_WORD_BYTE_AVAILABLE`.

Test signals: Four Predef test declarations expose each endian macro to generated tests.
