# sources/user-network-fs/samba/source3/printing/printspoolss.c

## Purpose

`printspoolss.c` bridges SMB print-file opens/writes/closes to the spoolss RPC server. It lets smbd write spool bytes to a local file for scalability and driver seek behavior while spoolss owns printer validation, job creation, final `EndDocPrinter`, and cancellation.

## Important APIs, Types, and Functions

- `struct print_file_data` stores service name, document name, spool filename, spoolss printer handle, 32-bit job ID, and 16-bit RAP job ID.
- `print_spool_rap_jobid()` returns the downlevel RAP job ID.
- `print_spool_open()` creates the spool file, opens the printer over spoolss, starts a document with `output_file`, maps the job to a RAP ID, and initializes the smbd `files_struct`.
- `print_spool_write()` writes bytes at SMB offsets and detects spoolss-side deletion by checking link count.
- `print_spool_end()` closes the printer on normal/shutdown close or terminates the job on error close.
- `print_spool_terminate()` removes RAP mapping and issues `spoolss_SetJob(...DELETE...)` followed by `ClosePrinter`.

## Control Flow

Open allocates per-file data under `fsp`, derives a Windows-like document name from the SMB filename, creates a temporary spool file in the printer path, opens a spoolss pipe, calls `OpenPrinter` with `PRINTER_ACCESS_USE`, and calls `StartDocPrinter` with level 1 document info using datatype `RAW` and the created output file. Once spoolss returns a job ID, `pjobid_to_rap()` creates the RAP mapping and the SMB file object is initialized as a write-only non-directory FSA-backed file.

Writes first `fstat()` the backing descriptor. If spoolss has unlinked the file as a cancellation signal, the descriptor is closed and `EBADF` is returned. For old SMB write semantics, offsets below the high 4GB chunk are rebased against the file size high bits. Failed writes terminate the spool job; successful writes return the byte count.

Close truncates the file if SMB delete-on-close is set, relying on spoolss end-doc cleanup to delete the zero-length job. Normal and shutdown close call `ClosePrinter`, which also ends the document. Error close calls `print_spool_terminate()`.

## State and Persistence

Per-open state lives in `fsp->print_file`; spool bytes live in a temporary file in the print share path. The long-lived spool job state is created by spoolss and lower print backend code. RAP mapping is in the in-memory TDB owned by `rap_jobid.c`.

## Dependencies and Integration Points

The file depends on `rpc_pipe_open_interface()`, generated spoolss client stubs, smbd `files_struct` setup, loadparm paths, FD handle helpers, security/session data, and RAP job-id mapping. It is called by SMB print-file open/write/close handling and relies on spoolss to call into the ordinary print job backend when `EndDocPrinter` happens.

## Risks and Edge Cases

- Open failure after `StartDocPrinter` must delete the spoolss job, so cleanup ordering is important.
- Link-count cancellation detection assumes spoolss communicates deletion by unlinking the file.
- The 4GB offset adjustment is compatibility logic and can be fragile with unusual write sequences.
- `print_spool_end()` assumes `conn->spoolss_pipe` remains valid.

## Test Signals

Integration tests should cover successful open/write/close, open failure cleanup after job creation, delete-on-close truncation, error-close cancellation, spoolss-side unlink during writes, RAP mapping cleanup, and large-offset SMB write behavior.
