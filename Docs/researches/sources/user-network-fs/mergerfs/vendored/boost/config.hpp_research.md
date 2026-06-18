<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config.hpp

## Purpose
This is the root Boost.Config include. It centralizes platform, compiler, standard-library, user, and suffix configuration so other Boost headers can test portable `BOOST_NO_*`, `BOOST_HAS_*`, and feature-helper macros.

## Important APIs, Types, And Control Flow
The header defines `BOOST_CONFIG_HPP`, selects a default `BOOST_USER_CONFIG` of `<boost/config/user.hpp>` unless disabled, includes user config first, then selects and includes compiler, standard library, and platform configs through detail selector headers unless they are already set or disabled. It always includes `boost/config/detail/suffix.hpp` last to derive secondary macros and fallback definitions, and uses `#pragma once` when `BOOST_HAS_PRAGMA_ONCE` is available.

## State And Persistence
All behavior is preprocessor state. It does not define runtime objects, functions, or persisted data.

## Dependencies And Integration Points
It integrates every vendored Boost header with the local compiler by including user, compiler, stdlib, platform, and suffix config headers. Mergerfs inherits Boost portability decisions through any include of Boost.Assert or other vendored Boost headers.

## Risks And Test Signals
Risks are macro-order dependent: user config must come first, suffix must come last, and disabling selector phases can leave required macros undefined. Test signals include preprocessing with `BOOST_NO_USER_CONFIG`, custom `BOOST_USER_CONFIG`, forced `BOOST_COMPILER_CONFIG`, and representative GCC/Clang builds that include headers depending on `BOOST_CONSTEXPR`, `BOOST_NOEXCEPT`, `BOOST_LIKELY`, and visibility macros.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config.hpp -->
