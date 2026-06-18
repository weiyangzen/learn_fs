# sources/distributed-fs/tahoe-lafs/misc/build_helpers/check-build.py

## Purpose

This helper validates build logs for the `test-desert-island` target. Its implemented mode checks that a build did not download packages from HTTP or HTTPS URLs.

## Important APIs, Types, and Functions

There are no reusable functions; it reads `sys.argv[1]` as a log file and `sys.argv[2]` as a mode. The only active mode is `no-downloads`, which flags lines beginning with `Downloading http:` or `Downloading https:`.

## Control Flow

The script initializes `good = True`, scans the build output line by line, prints offending download lines, and exits `0` with a success message or `1` with a failure message. It intentionally permits some `Reading` lines and local dependency references based on the comments.

## State, Dependencies, Integration, Risks, and Tests

There is no persistence beyond stdout and exit status. It depends only on Python stdlib and a build log path. Integration is Makefile/buildbot desert-island validation. Risks include trusting exact log prefixes, no argument validation, and no enforcement for metadata index reads. Test signals are small fixture logs with allowed local dependency references, disallowed HTTP/HTTPS downloads, and unknown modes.
