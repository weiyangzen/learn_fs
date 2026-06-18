# sources/test-tools/xfstests/tests/generic/752


Purpose: Checks that `exchangerange` refuses to operate on an active swap file.


Important APIs, helpers, and commands: Uses `_require_xfs_io_command exchangerange`, `MKSWAP_PROG`, `swapon`, `swapoff`, `punch-alternating`, and cleanup that turns swap off before deleting temp files.
 Local helper functions detected in the file include `_cleanup`.
 It imports `./common/filter`, `./common/preamble`.
 Capability gates include `_require_test`, `_require_xfs_io_command`.



Control flow, state, dependencies, risks, and test signals: The test creates a fragmented 32MiB file, makes it a swap file, creates a donor file, enables swap, and invokes xfs_io `exchangerange` from the swap file to the donor. State is the active swapfile and donor file under `$TEST_DIR`; cleanup must call swapoff. Dependencies are mkswap/swapon privileges and exchangerange support. Risks are leaving swap active on failure and differences in expected errno/output. Test signal is the exchangerange command output and no successful data exchange on swap-backed file. Source size is 44 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.
