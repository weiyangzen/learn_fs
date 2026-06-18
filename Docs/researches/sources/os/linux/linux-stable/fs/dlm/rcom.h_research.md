# File Research: sources/os/linux/linux-stable/fs/dlm/rcom.h

## Purpose
`rcom.h` declares the DLM recovery-communication API.

## Exports
- `dlm_rcom_status()`
- `dlm_rcom_names()`
- `dlm_send_rcom_lookup()`
- `dlm_send_rcom_lock()`
- `dlm_receive_rcom()`
- `dlm_send_ls_not_ready()`

## Notes
The header is used by recovery, directory, lock, and receive paths.
