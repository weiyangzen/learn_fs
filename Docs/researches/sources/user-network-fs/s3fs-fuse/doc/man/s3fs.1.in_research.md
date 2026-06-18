<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/doc/man/s3fs.1.in -->
# sources/user-network-fs/s3fs-fuse/doc/man/s3fs.1.in

Purpose: Source template for the `s3fs(1)` manual page documenting command syntax, authentication, mount options, utility modes, local storage behavior, performance considerations, and known S3 consistency caveats.

Important content: Documents mounting forms, unmounting commands, incomplete multipart upload utility modes, AWS credentials file and passwd file formats, environment-variable credentials, and a large set of `-o` mount options. Options cover ACLs, caching, storage class, SSE variants, credentials, public buckets, timeouts, stat cache/negative cache, TLS validation, multipart behavior, host/region/signature mode, permissions, threading, metadata/IAM modes, xattrs, compatibility modes, logging/debugging, and parent directory stat updates.

Control flow and integration: This is documentation, not executable code, but it must match option parsing and behavior in the s3fs binary. `@MAN_PAGE_DATE@` is substituted by `configure.ac` using the current build month/year. The manpage is installed through `doc/Makefile.am`.

State and persistence: Describes persistent credential files, local cache directories, temporary storage, log files, and multipart upload cleanup behavior. It also explains local cache deletion and disk-free controls.

Dependencies and integration points: Integrates with AWS S3 semantics, FUSE mount options, libcurl/TLS behavior, IAM/metadata services, object-store compatibility settings, and local cache/stat cache implementations.

Risks: The option surface is large, so drift between code and documentation is likely. Security-sensitive options such as `no_check_certificate`, `ssl_verify_hostname=0`, and `insecure_logging` are documented with warnings and should remain explicit. The BUGS section calls out S3 eventual consistency, a user-visible operational risk.

Test signals: Validate generated `man/s3fs.1` substitution, lint with manpage tools if available, and cross-check option names/defaults against s3fs help output and option parser tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/doc/man/s3fs.1.in -->
