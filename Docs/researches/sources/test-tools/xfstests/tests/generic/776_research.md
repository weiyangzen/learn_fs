# sources/test-tools/xfstests/tests/generic/776


Purpose: Runs fsx with atomic-write avoidance settings on filesystems/devices advertising atomic writes.


Important APIs, helpers, and commands: Defines `set_fsx_avoid`; uses `_run_fsx_on_file`, `_require_scratch_write_atomic`, `_require_odirect`, atomic write unit helpers, and FSX_AVOID flags.
 Local helper functions detected in the file include `set_fsx_avoid`.
 It imports `./common/atomicwrites`, `./common/preamble`.
 Capability gates include `_require_odirect`, `_require_scratch_write_atomic`.



Control flow, state, dependencies, risks, and test signals: The test mounts scratch, derives block and atomic max values, sets fsx avoid flags appropriate to the filesystem, then runs fsx against a scratch file. State is fsx model/data file and atomic write capability values. Dependencies are fsx, O_DIRECT, and scratch atomic support. Risks are filesystem-specific avoid flags and test coverage being too conservative. Success is fsx model consistency. Source size is 68 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.
