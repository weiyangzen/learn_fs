# sources/user-network-fs/samba/source3/lib/background.h

Purpose: declares the asynchronous recurring background-job API.

Important APIs/types/functions: forward declares `struct messaging_context`; exposes `background_job_send()` and `background_job_recv()`.

Control flow: callers create a tevent request with an event context, messaging context, optional trigger message list, initial delay, function pointer, and private data. The function returns seconds until the next run or `-1` to stop. Callers later receive final NTSTATUS through `background_job_recv()`.

State and persistence: no public state; implementation-owned request state is talloc-scoped to the returned `tevent_req`.

Dependencies/integration: includes `replace.h`, `<tevent.h>`, and `libcli/util/ntstatus.h`, making it usable by Samba daemons that already operate on tevent/messaging.

Risks/test signals: API users must ensure `private_data` is valid in forked child context and that `fn` is async-signal/fork aware. Header-level tests are compile/interface checks plus integration tests that schedule, trigger, and stop a background job.
