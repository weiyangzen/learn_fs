## sources/security-integrity/audit-userspace/src/ausearch-checkpt.c

Purpose: implements `ausearch --checkpoint`, persisting enough information to resume after the last complete output event.

Important APIs/functions: `set_ChkPtFileDetails()` records dev/inode of the input log; `set_ChkPtLastEvent()` records the last event timestamp, serial, type, and node; `save_ChkPt()` writes checkpoint text; `load_ChkPt()` reads it; `free_ChkPtMemory()` releases stored node strings. `parse_checkpt_event()` parses the `output=` line.

Control flow: `ausearch.c` loads checkpoint state at startup, compares future events against `chkpt_input_*`, updates `last_event` after processing events, records final file details, and writes the checkpoint if no checkpoint failure occurred.

State/persistence: persistent checkpoint file format is `dev=`, `inode=`, and `output=<node> <sec>.<milli>:<serial> 0x<type>`. Global/static state includes `checkpt_failure`, saved dev/inode, `last_event`, `chkpt_input_dev`, `chkpt_input_ino`, and `chkpt_input_levent`.

Dependencies/integration: depends on `event` from `ausearch-llist.h`, POSIX `stat()`, file I/O, and the checkpoint decision logic in `ausearch.c`.

Risks/test signals: checkpoint parsing mutates line buffers and uses `strtoull()` with limited end-pointer validation. `save_ChkPt()` overwrites directly rather than atomically. Corrupt or inode-reused files are detected later by event comparison. Tests should cover missing files, malformed lines, null node, node names, time_t size formats, inode reuse, and write failures.
