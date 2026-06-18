<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/language/objc.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/language/objc.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/language/objc.h` detects language-standard availability for a Boost.Predef language family.

## Important APIs, Types, and Functions

Primary macros are `BOOST_LANG_OBJC`. Related macros include `BOOST_LANG_OBJC`, `BOOST_LANG_OBJC_AVAILABLE`, `BOOST_LANG_OBJC_NAME`. Display-name macros are `BOOST_LANG_OBJC_NAME` "Objective-C". Direct includes are `boost/predef/version_number.h`, `boost/predef/make.h`, `boost/predef/detail/test.h`.

## Control Flow

The file initializes each language macro to `BOOST_VERSION_NUMBER_NOT_AVAILABLE`, then checks language predefined symbols such as `__OBJC__`. When a symbol is present it normalizes the value with `BOOST_PREDEF_MAKE_*` helpers or assigns `BOOST_VERSION_NUMBER_AVAILABLE`, defines `*_AVAILABLE`, and registers a Predef test.

## State and Persistence Behavior

No runtime state or persistence is involved. The macros reflect the language mode selected for the current translation unit, such as C++ standard level, CUDA compilation, or Objective-C enablement.

## Dependencies and Integration Points

Language detectors are included by `boost/predef/language.h` and the umbrella `boost/predef.h`. Vendored Boost users can use them to select code paths that require specific language front-end support.

## Risks and Edge Cases

Compiler-reported language macros can lag the actual supported features or use draft standard dates. CUDA and Objective-C modes may be enabled only for specific compiler phases. Code should compare against documented Predef versions rather than raw vendor values.

## Test Signals

Compile preprocessor probes under multiple language standards and front-end modes, then assert the expected `BOOST_LANG_*` value and `*_AVAILABLE` marker. Negative tests should compile in modes where the language extension is absent.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/language/objc.h -->
