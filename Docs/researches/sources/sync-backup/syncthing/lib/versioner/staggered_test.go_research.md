# sources/sync-backup/syncthing/lib/versioner/staggered_test.go

Purpose: validates staggered retention interval math and archive path creation.

Important tests: `TestStaggeredVersioningVersionCount` defines a fixed `now`, a dense set of timestamped versions across seconds, hours, days, weeks, and over max age, then expects a precise delete list after `toRemove`. It sorts expected and actual lists and uses `messagediff`. `TestCreateVersionPath` configures a nested versions directory, archives a file, and confirms a version file is created under that directory.

State and persistence: fixed timestamp strings and temp directory archive writes.

Dependencies and integration: exercises `newStaggered`, timestamp parsing, and archive helper integration.

Risks and signals: high-signal retention coverage, including leap-year comments. It does not test restore or cleanup context cancellation.
