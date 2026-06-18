# File Research: sources/os/plan9/plan9/sys/src/cmd/9nfs/9auth.c

Purpose: small host-side helper for manual challenge/response auth files exposed by 9nfs.

Key behavior: parses root/user/debug/delete options, builds `<root>/#<user>`, optionally creates it for deletion/reset, otherwise reads a challenge, prompts for a response, rewinds, and writes the response.

Integration notes: standalone Unix-style utility using libc/POSIX headers rather than Plan 9 `all.h`. Works with `NETCHLEN` fixed-size challenge/response records.
