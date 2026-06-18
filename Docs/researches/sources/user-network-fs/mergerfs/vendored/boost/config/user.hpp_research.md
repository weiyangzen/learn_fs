# sources/user-network-fs/mergerfs/vendored/boost/config/user.hpp

Purpose: template site-configuration header for Boost users. It is intentionally unmodified in Boost distributions and documents user-overridable config macros.

Important APIs/macros: it does not define active macros by default. Comments describe overrides such as `BOOST_COMPILER_CONFIG`, `BOOST_STDLIB_CONFIG`, `BOOST_PLATFORM_CONFIG`, `BOOST_NO_*_CONFIG`, `BOOST_NO_CONFIG`, `BOOST_STRICT_CONFIG`, `BOOST_ASSERT_CONFIG`, `BOOST_DISABLE_THREADS`, `BOOST_DISABLE_WIN32`, ABI prefix/suffix overrides, dynamic-link controls (`BOOST_ALL_DYN_LINK`, `BOOST_WHATEVER_DYN_LINK`), auto-link disables (`BOOST_ALL_NO_LIB`, `BOOST_WHATEVER_NO_LIB`), and `BOOST_LIB_BUILDID`.

Control flow/dependencies: no includes or active conditionals. It is included by Boost.Config as a customization point.

State and persistence: none by default; if users edit/copy it, it controls compile-time configuration for all translation units that include Boost.

Integration points: the first policy layer for `boost/config.hpp`, preceding automatic compiler/platform/stdlib selection.

Risks and test signals: risk is inconsistent local edits across translation units, causing ABI or feature mismatches. Test by auditing build defines and ensuring user overrides are centralized and identical for all Boost-consuming targets.
