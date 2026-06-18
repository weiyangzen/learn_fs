# sources/sync-backup/syncthing/etc/solaris-smf/syncthing.xml

## Purpose
This XML file is a Solaris Service Management Facility manifest for running Syncthing as `site/syncthing`. It defines service dependencies, credentials, start/stop methods, and SMF metadata.

## Important APIs, Types, And Functions
The manifest uses the SMF service bundle DTD. It declares a single-instance service with a default enabled instance, dependencies on `svc:/milestone/network:default` and `svc:/system/filesystem/local`, method credentials `user="jb" group="other"`, a start method executing `/home/jb/bin/syncthing`, a stop method `:kill`, and framework properties `duration=child` plus `ignore_error=core,signal`.

## Control Flow
SMF imports the manifest and starts the default instance once network and local filesystem dependencies are satisfied. The start method runs Syncthing with `HOME=/home/jb` and `STNORESTART=1` in the method environment. SMF tracks the child process and uses `:kill` for stop.

## State And Persistence Behavior
Syncthing state is under `/home/jb` by default. The manifest persists service configuration in the SMF repository after import. Runtime logs and restarts are governed by SMF and Syncthing defaults.

## Dependencies And Integration Points
It integrates with Solaris SMF, service dependencies, method credentials, and Syncthing's binary/environment. `STNORESTART=1` delegates supervision to SMF. The unsupported perfstats Go file also treats Solaris specially, so this platform has distinct runtime support considerations.

## Risks And Edge Cases
The manifest is strongly example-specific: user `jb`, group `other`, binary path `/home/jb/bin/syncthing`, and home directory all need customization. XML whitespace includes a visibly misaligned `HOME` envvar line but remains structurally valid. If SMF duration or restart semantics do not match Syncthing's foreground behavior, supervision may be unreliable.

## Test Signals
Validation should import the manifest with SMF tools, inspect service properties, start/stop the service, and confirm the process runs as the intended user with the intended home directory. XML validation against the SMF DTD can catch structural errors.
