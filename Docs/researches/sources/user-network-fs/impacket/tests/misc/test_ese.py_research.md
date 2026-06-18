# sources/user-network-fs/impacket/tests/misc/test_ese.py

Purpose: Tests ESENT large-page tag parsing, especially high-bit reserved tag state.

Important APIs, types, and functions: Uses `ESENT_PAGE`, `ESENT_PAGE_HEADER`, `FIRST_AVAILABLE_PAGE_TAG_MASK`, and `FIRST_AVAILABLE_PAGE_TAG_RESERVED_SHIFT`. Helper `_build_page` constructs synthetic 32 KiB pages.

Control flow: Builds page headers and trailing page tags with controlled `FirstAvailablePageTag` values, then verifies tag count/reserved splitting, tag retrieval, bounds errors, and data-tag iteration skipping reserved tags.

State and persistence behavior: Pure in-memory synthetic page bytes. No ESE files are read.

Dependencies and integration points: Protects ESE database page parsing used by offline database readers.

Risks: Large page tag metadata packs reserved and count bits together; misinterpreting high bits can expose reserved tags as records or break iteration.

Test signals: Strong targeted regression signal for high-bit tag state, reserved tag skipping, tag payload lookup, and invalid tag errors.
