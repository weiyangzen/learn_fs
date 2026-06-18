# sources/user-network-fs/impacket/tests/dcerpc/test_tsch.py

## Purpose
This file tests three related scheduled-task RPC interfaces: legacy ATSVC (`atsvc`), task account security (`sasec`), and modern Task Scheduler Service (`tsch`). It validates job add/enum/get/delete, account credential calls, task scheduler version/retrieve/folder/enum/run/instance/stop/rename/runtime/info/enabled APIs, and both raw request and helper wrapper paths.

## Important APIs, Types, and Functions
`ATSVCTests`, `SASECTests`, and `TSCHTests` all inherit `DCERPCTests`, bind to `\\PIPE\\atsvc`, authenticate, and request packet privacy. `AT_INFO` is the common ATSVC job structure. `TSCHTests.get_tsch_test_path()` generates unique folder names with UUIDs, and `delete_tsch_test_path()` tolerates missing-path errors. Tests use `tsch` request classes and helpers such as `hSchRpcCreateFolder`, `hSchRpcEnumTasks`, `hSchRpcRun`, and `hSchRpcEnableTask`.

## Control Flow
ATSVC tests create jobs that run command-shell output redirection, enumerate or query them, then delete by job id. TSCH tests often open a second DCE connection to ATSVC to create an `AtN` job, then use TSCH to retrieve, enumerate, run, inspect, or stop that task before deleting it through ATSVC. Folder tests create a random scheduler folder, enumerate root folders, and delete in `finally`. Many tests catch `ERROR_NOT_SUPPORTED`, missing-path HRESULTs, `SCHED_E_TASK_NOT_RUNNING`, `ERROR_INVALID_FUNCTION`, or `E_NOTIMPL` as acceptable environment outcomes.

## State and Persistence Behavior
The file creates scheduled jobs, temporary scheduler folders, and may run tasks that write output under `%SYSTEMROOT%\\Temp\\BTO` or `%SYSTEMROOT%\\Temp\\ANI`. It also sets task scheduler account information through SASEC using configured test credentials. Some job cleanup is explicit after successful setup, but not always protected by `finally`, so a failure between add and delete can leave jobs or output files on the target.

## Dependencies and Integration Points
The suite depends on Impacket's `tsch`, `atsvc`, and `sasec` modules, `impacket.system_errors.ERROR_NOT_SUPPORTED`, shared credentials, UUID generation, Windows Task Scheduler/AT service support level, and the presence of sample built-in task `\\Microsoft\\Windows\\Defrag\\ScheduledDefrag`. It exposes remote SMB transport classes for NDR and NDR64 for each interface class.

## Risks
Remote task creation and execution is high impact. Tests can execute command lines on the target, alter scheduler account settings, enable built-in tasks, and leave scheduler artifacts if cleanup is bypassed. Many APIs are OS-version dependent, so the suite intentionally accepts unsupported/not-implemented responses. Some tests print and pass on broad TSCH errors, reducing failure precision.

## Test Signals
Signals include successful ATSVC job lifecycle, TSCH visibility of legacy AT jobs, unique folder create/enumerate/delete behavior, task run GUID handling, expected scheduler not-running/not-scheduled states, account-info calls accepting or returning expected missing-file errors, and helper/raw API parity. Skipped `SchRpcRegisterTask` documents an unimplemented/disabled test area.
