# File Research: sources/os/plan9/9front/sys/src/cmd/ip/httpfile.c

9P filesystem that exposes an HTTP URL as a read-only file. It uses `/mnt/web` to issue HEAD for content length and GET requests with Range headers for block-sized reads.

The server maintains a block cache and an in-progress queue, serializes HTTP range fetches through worker threads, satisfies queued 9P read requests from cached blocks, and supports flush by removing pending reads. It can post a srv file or mount at a mount point, with configurable cache size and displayed filename.
