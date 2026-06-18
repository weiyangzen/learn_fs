# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/kcs/tracker.go

Purpose: KCS lifecycle tracker that keeps the compile server available while needed and shuts it down after idle periods.

Important flow: periodically checks for active builds/bisectors and server/debug settings, updates status, and initiates VM shutdown or cleanup when KCS is idle long enough. It integrates with `server.accessKCS` assumptions that LTM launches KCS and checks shutdown metadata before relaunch.

State and dependencies: depends on KCS in-memory maps, logging paths, GCE metadata/config, and likely the appliance shutdown path. It coordinates with `main.go` through a `finished` channel so the KCS server can stop when tracker decides the instance is done.

Integration points: LTM `SendInternalRequest` may launch or relaunch KCS through `gce-xfstests launch-kcs`; tracker prevents abandoned KCS instances from persisting after build/bisect work.

Risks and test signals: because build state is in-memory, tracker decisions after process restart can differ from existing external work. Tests should cover idle timeout with and without active bisectors, debug mode behavior, and shutdown metadata interactions.
