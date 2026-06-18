# sources/user-network-fs/mergerfs/vendored/boost/predef/platform/cloudabi.h

Purpose: Detects the CloudABI platform.

Important APIs, types, and functions: Defines `BOOST_PLAT_CLOUDABI`, `BOOST_PLAT_CLOUDABI_AVAILABLE`, and `BOOST_PLAT_CLOUDABI_NAME`.

Control flow: The macro starts unavailable and becomes available when `__CloudABI__` is defined. On success it includes `platform_detected.h`.

State and persistence behavior: Compile-time-only; no persistent or runtime behavior.

Dependencies and integration points: Included by `boost/predef/platform.h` and can be combined with compiler/architecture detectors for target-specific code.

Risks: CloudABI is a niche target; stale or missing compiler predefined macros would leave detection unavailable. It reports availability, not a version.

Test signals: The file declares the standard Boost.Predef test macro for generated validation.
