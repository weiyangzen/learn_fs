# sources/sync-backup/git-lfs/tq/ssh.go

Purpose: SSH batch client and SSH transfer adapter for Git LFS object transfers over SSH multiplexed connections.

Important APIs/types/functions: `SSHAdapterName`, `SSHBatchClient`, `Batch`, `batchInternal`, `SSHAdapter`, `WorkerStarting`, `DoTransfer`, `download`, `doDownload`, `upload`, `doUpload`, `verifyUpload`, `argumentsForTransfer`, `Begin`, `Trace`, and `configureSSHAdapter`.

Control flow: batch requests send OID/size lines over SSH, parse status/args/lines into `BatchResponse` and actions. Adapter workers reserve SSH connections by worker number. Downloads issue `get-object`, validate status and size arg, copy data through hashing reader, verify OID, and rename into place. Uploads send `put-object` with data and verify with `verify-object`, mapping 403/429 to retriable errors.

State and persistence: uses SSH connection locks, temp files under incomplete storage for downloads, and local object files for uploads.

Dependencies and integration points: manifest swaps batch client to `SSHBatchClient` when API client has SSH transfer; adapter registered for upload/download. Uses `tools` copy/hash/temp helpers and `ssh.SSHTransfer`.

Risks: line parsing sorts server response lines and groups by OID; malformed lines fail the whole batch. Connection locking serializes per connection. Missing SSH transfer causes worker startup failure.

Test signals: `ssh_test.go` covers nil transfer startup error; broader SSH protocol paths are not tested in this subset.
