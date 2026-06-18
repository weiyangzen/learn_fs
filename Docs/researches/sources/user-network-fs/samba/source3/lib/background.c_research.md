# sources/user-network-fs/samba/source3/lib/background.c

Purpose: runs recurring background jobs by forking child helpers from a tevent parent, with optional messaging triggers to wake the schedule early.

Important APIs/types/functions: `struct background_job_state`, `background_job_send()`, `background_job_recv()`, trigger filter `background_job_trigger()`, wait callback `background_job_waited()`, completion callback `background_job_done()`, and destructor.

Control flow: `background_job_send()` registers filtered messaging reads for configured message IDs and schedules the initial wakeup. On wakeup it creates a pipe, forks, reinitializes messaging/event state in the child, runs `fn(private_data)`, writes the returned wait seconds to the pipe, and exits. The parent asynchronously reads the integer; `-1` completes the request, otherwise a new wakeup is scheduled.

State and persistence: state is talloc-owned and keeps trigger IDs, the active wakeup request, child result pipe fd, and pending pipe read. No durable persistence is used.

Dependencies/integration: tevent requests/timers, Samba messaging, `read_packet_send`, fork/pipe, `reinit_after_fork()`, NTSTATUS helpers.

Risks/test signals: child only reports a single integer and exits, so failures before pipe write surface as read/NT errors. Destructor must close pipe/read state during cancellation. Tests should cover initial delay, trigger wakeup, repeating return values, `-1` stop, fork/pipe errors, callback failure after fork reinit, and cancellation cleanup.
