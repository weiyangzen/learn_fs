# sources/user-network-fs/mergerfs/vendored/boost/unordered/detail/bad_archive_exception.hpp

Purpose: Reports invalid or corrupted Boost.Unordered serialization archives.

Important APIs, types, and functions: Defines `boost::unordered::detail::bad_archive_exception`, deriving from `std::runtime_error`, with the fixed message `Invalid or corrupted archive`.

Control flow: No branching; default construction initializes the base error message.

State and persistence behavior: Exception object contains only `std::runtime_error` message state.

Dependencies and integration points: Included by concurrent table serialization loading; thrown via `boost::throw_exception` when duplicate keys are found in an archive.

Risks: The exception does not include the offending key or archive position, so diagnostics are intentionally minimal.

Test signals: Load tests should feed duplicate/corrupted archive entries and assert this exception path.
