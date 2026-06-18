# sources/user-network-fs/mergerfs/vendored/boost/throw_exception.hpp

Purpose: Centralizes Boost exception throwing, exception wrapping, source-location capture, and no-exception customization.

Important APIs, types, and functions: Exposes `boost::throw_exception`, `BOOST_THROW_EXCEPTION(x)`, `boost::wrapexcept<E>`, `boost::throw_with_location`, and `boost::get_throw_location`. In `BOOST_NO_EXCEPTIONS` builds, users must provide `throw_exception(std::exception const&)` overloads.

Control flow: With exceptions enabled and `BOOST_EXCEPTION_DISABLE` unset, `throw_exception` checks that `E` is compatible with `std::exception` and throws `wrapexcept<E>`, which inherits from `E`, conditionally from `boost::exception`, and conditionally from `clone_base`. Location-aware overloads attach file, line, function, and column through Boost.Exception metadata. `throw_with_location` throws a lightweight `with_throw_location<E>` wrapper, and `get_throw_location` recovers that location via RTTI or Boost.Exception metadata.

State and persistence behavior: No global state. Exception objects persist throw metadata inside the thrown object. `clone()` uses heap allocation guarded by a local deleter for exception safety.

Dependencies and integration points: Depends on Boost.Exception, Boost.Assert source locations, Boost.Config, standard `<exception>`, and type traits. Used broadly by Boost code, including unordered archive validation.

Risks: Requires thrown Boost exceptions to derive from `std::exception`. Behavior differs materially under `BOOST_NO_EXCEPTIONS`, `BOOST_EXCEPTION_DISABLE`, and `BOOST_NO_RTTI`. Wrapping changes the dynamic type caught by exact-type handlers.

Test signals: Compile tests should cover normal throw/catch, source-location recovery, no-RTTI fallback, disabled Boost.Exception wrapping, and no-exceptions user hooks.
