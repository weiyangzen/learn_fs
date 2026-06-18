# File Research: sources/os/plan9/plan9/sys/src/cmd/fossil/dump.c

Small daemon-style helper for periodic fossil snapshots and archives.

It opens a fossil console, changes into a mounted fossil namespace, forks into the background, optionally waits for clock stabilization, and periodically writes console commands. It triggers daily archival snapshots if the expected `/archive/yyyy/mmdd` path is absent and, unless archive-only mode is selected, triggers regular snapshots at the configured interval.

This is described in-code as a clumsy helper rather than core server logic.
