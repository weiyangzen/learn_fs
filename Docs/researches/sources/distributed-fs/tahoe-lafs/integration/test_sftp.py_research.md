# sources/distributed-fs/tahoe-lafs/integration/test_sftp.py

## Purpose
Validates Tahoe-LAFS SFTP access using Paramiko: authentication behavior, SSH-key login, file read/write, directory mutation, and rename semantics.

## Important APIs, Types, and Functions
`connect_sftp` creates a Paramiko `SSHClient`, disables agent/key discovery, accepts host keys automatically, and returns an `SFTPClient`. It also recursively removes previous root contents. `sftp_client_key` loads Alice's generated private key from `private/ssh_client_rsa_key`. Tests use `generate_ssh_key` for bad-key setup and `run_in_thread` around blocking Paramiko calls.

## Control Flow
Authentication tests attempt invalid usernames/passwords and invalid key/username combinations, expecting `AuthenticationException`. The positive key test logs in as `alice-key` and expects an empty directory. File tests write bytes in multiple calls and read them back in chunks. Directory tests create a child directory, create files, change directories, read nested files, remove files, and attempt directory removal. Rename tests create `dir/file`, rename the file and then the directory, and read content at the final path.

## State and Persistence
All SFTP operations modify Tahoe mutable directory state exposed as Alice's SFTP root. `connect_sftp` tries to clean the root before each test, which mutates shared state and reduces test isolation issues from previous failures.

## Dependencies and Integration Points
Depends on Alice's Tahoe SFTP server listening on localhost port 8022, Paramiko transport/SFTP implementation, Tahoe account configuration for `alice-key`, and the test helper SSH key material.

## Risks
The hard-coded port 8022 can conflict or fail if Alice's fixture changes. Recursive root cleanup may mask leakage between tests and can be destructive within the test grid. `AutoAddPolicy` is acceptable for local integration tests but does not validate host identity.

## Test Signals
Signals are Paramiko authentication failures/successes, exact byte reads, directory listings, and successful final reads after file and directory renames.
