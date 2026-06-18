# sources/user-network-fs/mergerfs/vendored/boost/core/yield_primitives.hpp

Purpose: Aggregating header for Boost.Core spin/yield/sleep primitives.

Important APIs, types, and functions: Includes `sp_thread_pause`, `sp_thread_yield`, and `sp_thread_sleep`.

Control flow: None in this header; behavior comes from included platform detail headers.

State and persistence behavior: No state.

Dependencies and integration points: Public include point for code that needs all backoff primitives.

Risks: Pulls platform-specific declarations into translation units; include-order issues would surface from detail headers.

Test signals: Include-only compile test and smoke calls to the three primitives on supported platforms.
