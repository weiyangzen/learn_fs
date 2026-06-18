# sources/user-network-fs/mergerfs/vendored/boost/config/header_deprecated.hpp

Purpose: provides a portable macro for marking a header as deprecated.

Important APIs/macros: defines `BOOST_HEADER_DEPRECATED(a)`. Unless `BOOST_ALLOW_DEPRECATED_HEADERS` or `BOOST_ALLOW_DEPRECATED` is defined, the macro emits a pragma message saying that the header is deprecated and naming the replacement argument `a`.

Control flow/dependencies: includes `boost/config/pragma_message.hpp`, then conditionally defines the macro. It is C-compatible and has a normal include guard.

State and persistence: no runtime state; it only affects compile diagnostics.

Integration points: deprecated Boost headers include this file and pass the replacement header string. `BOOST_PRAGMA_MESSAGE` handles compiler-specific diagnostic syntax.

Risks and test signals: risk is warning noise or unsupported pragma syntax, both delegated to `pragma_message.hpp`. Test by preprocessing or compiling a deprecated wrapper with and without `BOOST_ALLOW_DEPRECATED_HEADERS`.
