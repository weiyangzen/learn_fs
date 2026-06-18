# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsState.cc

Purpose: implements global CMS state monitoring for suspend and staging availability. It computes aggregate state from admin files, node counts, frontend health, disk space, and staging count, then broadcasts status changes to managers/redirectors.

Important APIs/functions: global `XrdCms::CmsState`; constructor initializes suspended/no-stage defaults. `Enable()` samples admin files and forces first notification. `Monitor()` waits for state changes and sends `kYR_status` updates through `RTable` and `XrdCmsManager::Inform`. `Port()` returns the frontend data port. `sendState()` sends current suspend/stage state to a link. `Set()` configures minimum node count and admin file paths. `Status()` converts bit changes into protocol modifiers and logs transitions. `Update()` changes state inputs for active counts, staging counts, frontend status, space, and admin stage/suspend controls.

Control flow: state changes call `Update()`, which recomputes `currState`, `Suspended`, and `NoStaging`; if enabled and changed, it posts the monitor semaphore. `Monitor()` calculates deltas from `prevState`, formats modifiers, optionally embeds the data port on resume, broadcasts to redirectors when appropriate, and informs managers.

State and persistence: in-memory counters/flags plus admin sentinel files `NOSTAGE` and `SUSPEND` under configured admin path. `Update(Stage/Active)` creates or unlinks those files to reflect administrative state. `NoStageFile` and `SuspendFile` are allocated strings.

Dependencies/integration: uses CMS protocol status structs, `XrdLink`, `XrdCmsManager`, `RTable`, trace logging, POSIX `stat/open/unlink`, and semaphores/mutexes.

Risks: `Set(ncount,isman,AdminPath)` uses fixed `fnbuff[1048]` with `strcpy`; long admin paths can overflow. `Update(Active)` has duplicated unlink branches that may be intentional but should be reviewed. `sendState()` sends only the header size rather than the full `CmsStatusRequest`, matching its zero-datalen header but worth preserving in tests. Monitor is an infinite loop with process-lifetime ownership.

Test signals: admin file creation/removal tests, state transition matrix for suspend/no-stage/frontend/space/counts, redirector broadcast tests, initial `Enable()` notification, and long admin path validation.
