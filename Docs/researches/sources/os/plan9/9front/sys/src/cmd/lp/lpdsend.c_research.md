# File Research: sources/os/plan9/9front/sys/src/cmd/lp/lpdsend.c

`lpdsend` sends jobs to an LPD-style printer service. It supports sending a print job, checking queue status, and killing a job.

Key behavior:
- Options include printer name, user, host, sequence number, file type, debug, queue status, and kill target.
- For stdin jobs, it copies input to a temporary local file before opening the network connection.
- Dials `tcp!host!printer` using privileged-style source ports 721-731.
- Sends RFC1179-like receive-job, data-file, and control-file records, waiting for NUL ACKs after each stage.
- Status and kill paths send the corresponding control request and copy the response to stderr.
- `copyfile()` reports progress every 5 percent when total size is known and is guarded by a long alarm timeout.

This is portable C with Plan 9 networking compatibility. It assumes cooperative printer protocol behavior and uses `tmpnam()` for stdin staging.
