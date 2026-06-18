## sources/user-network-fs/blobfuse2/component/xload/stats_manager_test.go

Purpose: Unit/integration tests for stats manager construction, JSON file export, processing, and stop behavior.

Important APIs and flow: `TestNewStatsManager` confirms non-export mode leaves `fileHandle` nil and export mode creates a file, then removes it. `TestStatsManagerStartStop` starts an exporting stats manager, sends lister, directory, stats-manager, invalid component, data-manager, and splitter events, sleeps to allow exporter ticks, stops the manager, and asserts directory count, total processed count, and positive transfer counters.

State and dependencies: Uses the default blobfuse work directory for JSON output and real time sleeps. Logging is silenced.

Risks and test signals: The test depends on ticker timing and can run for roughly 15 seconds. It validates aggregate counters but does not inspect JSON validity or bandwidth values. Race cases around `Stop`, closed channels, and automatic `done` signaling are not covered.
