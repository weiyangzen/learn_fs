# sources/user-network-fs/mergerfs/vendored/boost/config/platform/wasm.hpp

Purpose: configures Boost for WebAssembly targets.

Important APIs/macros: defines `BOOST_PLATFORM "Wasm"`, uses `__has_include(<unistd.h>)` to set `BOOST_HAS_UNISTD_H`, includes POSIX feature detection, and defines `BOOST_NO_FENV_H` because fenv lacks the expected C++11 macros.

Control flow/dependencies: optional unistd detection, then `boost/config/detail/posix_features.hpp`, then fenv correction.

State and persistence: compile-time macro state only.

Integration points: selected by `__wasm__`. Feeds platform identity and conservative fenv capability into Boost.Math and other numeric code.

Risks and test signals: WebAssembly environments vary by libc (Emscripten, WASI, custom). Test unistd presence, POSIX macro derivation, fenv header behavior, pthread modes, and standard-library header availability per target.
