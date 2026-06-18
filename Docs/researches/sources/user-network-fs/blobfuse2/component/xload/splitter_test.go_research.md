## sources/user-network-fs/blobfuse2/component/xload/splitter_test.go

Purpose: Tests splitter creation, skip behavior, end-to-end file downloads, and MD5 consistency through a lister-splitter-data-manager chain.

Important APIs and flow: Suite setup creates a random loopback remote tree with root and nested files. `setupTestSplitter` creates local cache path, small block pool, lock map, and stats manager. `TestNewDownloadSplitter` checks validation and successful construction. `TestProcessFilePresent` verifies directory conflict error and same-size local file skip. `TestSplitterStartStop` wires lister, splitter, and remote data manager, starts all stages, sleeps, stops lister, and validates recursive MD5 equality. `TestSplitterConsistency` enables loopback MD5 publication and splitter validation.

State and dependencies: Uses real temp directories, loopback, `exec.Command("cp")`, small mmap blocks, stats manager, and sleep-based completion.

Risks and test signals: Failure cases are explicitly left as TODO. Tests do not stop all components in `TestSplitterStartStop`, relying on cleanup side effects. Sleep timing may be flaky. Positive integration coverage is strong for the download pipeline.
