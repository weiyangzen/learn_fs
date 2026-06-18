# sources/user-network-fs/mergerfs/vendored/boost/core/serialization.hpp

Purpose: Minimal serialization adapter utilities for Boost.Core users that need split load/save dispatch without taking a full serialization dependency.

Important APIs, types, and functions: Forward declarations for `boost::serialization::version`, `access`, `nvp`; `core_version_type`; `boost::core::split_free`, `split_member`, `load_construct_data_adl`, and `save_construct_data_adl`; internal `load_or_save_f` and `load_or_save_m`.

Control flow: `split_free` and `split_member` inspect `Archive::is_saving::value` at compile time and call either `save`/`load` free functions or member functions through `serialization::access`.

State and persistence behavior: No state; all persistence belongs to the archive and serialized object.

Dependencies and integration points: Includes `nvp.hpp`. Integrates with archive types that expose `is_saving` and Boost.Serialization conventions.

Risks: Requires exact archive traits and access hooks. ADL construction hooks are no-ops by default and need customization elsewhere for non-default construction.

Test signals: Mock saving/loading archives, split free/member functions, version propagation, and ADL override checks for construct data.
