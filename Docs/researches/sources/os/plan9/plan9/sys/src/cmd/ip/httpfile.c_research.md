# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/httpfile.c

9P filesystem that exposes an HTTP or HTTPS URL as a read-only file. It parses the URL, uses HEAD to discover content length, and serves a synthetic root directory containing one file named from the URL or `-f`.

Reads are satisfied from 64 KiB cached blocks fetched via HTTP Range GETs. The server maintains cache and in-progress block queues, serializes range fetches through worker threads, serves queued 9P reads when blocks arrive, supports flush interruption, and can post a srv file or mount at a mount point.
