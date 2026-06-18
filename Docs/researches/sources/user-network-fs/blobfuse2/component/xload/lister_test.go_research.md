## sources/user-network-fs/blobfuse2/component/xload/lister_test.go

Purpose: Integration-style tests for remote lister behavior using loopback as the remote namespace.

Important APIs and flow: Suite setup creates a random `/tmp/xload_*` remote tree with ten files and ten directories containing five files each, configures loopback, and starts silent logging. `testComponent` counts scheduled file work items through an `XBase` thread pool. `TestNewRemoteLister` validates option failures and success. `TestListerStartStop` chains lister to the counting component, starts it, sleeps five seconds, stops it, expects 60 file schedules, and verifies ten local directories. `TestListerMkdir` directly tests directory creation.

State and dependencies: Uses real temporary directories, loopback, global `lb` and `lb_path`, stats manager, and wall-clock sleeps.

Risks and test signals: Sleep-based synchronization can be flaky on slow systems. The expected count depends on full recursive listing completion. Error paths from `StreamDir`, downstream `Schedule`, and initial list-delay config are not deeply covered.
