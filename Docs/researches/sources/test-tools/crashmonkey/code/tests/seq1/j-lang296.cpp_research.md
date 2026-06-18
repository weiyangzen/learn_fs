<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang296.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang296.cpp

Purpose: Exercises CrashMonkey crash-consistency behavior for rename directory A to B, then global sync. This is one generated C++ test in the seq1 family, focused on the `directory-rename/sync` scenario.

Important APIs/types/functions: BaseTestCase virtual methods setup(), run(int checkpoint), and check_test(); CrashMonkey wrapper calls cm_->CmOpen, CmClose, CmFsync, CmFdatasync, CmRename, CmSync, and CmCheckpoint; POSIX calls include mkdir plus the scenario-specific fallocate, truncate, fsetxattr, or removexattr when present. Paths are stored as std::string members derived from mnt_dir_.

Control flow: setup() initializes all path members from mnt_dir_. run() repeats that initialization, sets local_checkpoint to zero, then performs: mkdir A; open and close A directory; rename A to B; CmSync; checkpoint. After CmCheckpoint succeeds, it increments local_checkpoint and can return 1 to tell the harness to stop at checkpoint 1; otherwise it closes remaining descriptors and returns 0. check_test() has no file-content or metadata assertions of its own.

State and persistence behavior: directory rename durability under sync. State is confined to the mounted test directory and the CrashMonkey checkpoint stream. setup() and run() rebuild canonical paths for /A, /B, /foo, /bar, A/foo, A/bar, B/foo, B/bar, A/C/foo, and A/C/bar. run() executes one mutation sequence, calls exactly one CmCheckpoint, increments local_checkpoint, and returns 1 when the requested crash point is reached. check_test() only reconstructs paths and returns 0, so oracle comparison is delegated to the surrounding CrashMonkey harness rather than local assertions.

Dependencies and integration points: The test is exported through extern "C" test_case_get_instance() and test_case_delete_instance(), allowing the CrashMonkey loader to instantiate this generated class polymorphically as a BaseTestCase. It depends on Linux/POSIX headers for file, directory, allocation, truncate, and xattr behavior and on user_tools/api/workload.h for WriteData in data-writing cases.

Risks and edge cases: The main risks are weak local oracle coverage, repeated generated boilerplate, and subtle differences between file fsync, directory fsync, fdatasync, and global sync semantics. Error paths return errno immediately; some open-failure branches call CmClose on a negative descriptor, so harness wrappers must tolerate that generated pattern. Because the checkpoint happens before final close in many cases, the harness is specifically probing crash images at the post-sync/pre-close boundary.

Test signals: A successful normal run returns 0 and a successful checkpoint-interrupted run returns 1 at checkpoint 1. Failures surface as negative CrashMonkey wrapper results, POSIX errno returns, failed checkpoint creation, loader failures for the extern C factory functions, or downstream CrashMonkey/replay mismatches for the persisted namespace, data blocks, xattrs, or file size.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang296.cpp -->
