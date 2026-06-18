<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/ftp-server-driver.go -->
# sources/object-store/minio/cmd/ftp-server-driver.go

## Purpose
Implements the goftp server driver that maps FTP filesystem operations to MinIO S3 operations through the MinIO Go client. It also authenticates FTP users against MinIO IAM or LDAP and publishes FTP trace metrics.

## Important APIs, types, and functions
- `ftpDriver` implements `ftp.Driver`; `NewFTPDriver` points it at local MinIO API address.
- Path helpers `buildMinioPath` and `buildMinioDir` normalize FTP paths to bucket/object paths.
- `minioFileInfo` adapts `minio.ObjectInfo` to `os.FileInfo`.
- `ftpTrace`, `ftpMetrics.log`, and `globalFtpMetrics` publish trace events.
- Driver methods implement `Stat`, `ListDir`, `CheckPasswd`, `getMinIOClient`, `DeleteDir`, `DeleteFile`, `Rename`, `MakeDir`, `GetFile`, and `PutFile`.

## Control flow
Each FTP operation logs a trace through a deferred closure, obtains a MinIO client for the FTP session, converts the FTP path into bucket/object components, and invokes S3 APIs. Root listing lists buckets; bucket paths check bucket existence or create/delete buckets; object paths stat/list/get/put/remove objects. LDAP login can bind directly or mint temporary STS credentials with LDAP claims and site-replication hooks. Non-LDAP users use stored access/secret keys, while temporary credentials are rejected for normal IAM users.

## State and persistence behavior
Persistence happens through MinIO object operations: bucket creation/removal, zero-byte directory marker objects, object upload/download/delete, and recursive directory deletion by listing and removing objects. LDAP temporary users may be persisted in IAM state and replicated. Trace events include user, command, parameters, login state, source, path, duration, bytes, and error.

## Dependencies and integration points
Depends on `goftp.io/server/v2`, MinIO Go client, IAM/LDAP systems, site replication IAM hook, remote-target HTTP transport with forwarded client IP, madmin trace pubsub, MIME database, and MinIO path/bucket helpers.

## Risks and edge cases
FTP semantics do not perfectly match object storage: directories are markers or prefixes, rename and append are not implemented, `Stat` returns a dummy directory on `NoSuchKey` to satisfy LIST behavior, and recursive delete can fail silently if the listing goroutine sees an error before sending it. LDAP credential minting and policy checks are security-sensitive.

## Test signals
No direct tests in this group. Expected signals are FTP integration tests for login, bucket/object list/stat, upload/download/delete, TLS forwarding, LDAP behavior, and trace emission.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/ftp-server-driver.go -->
