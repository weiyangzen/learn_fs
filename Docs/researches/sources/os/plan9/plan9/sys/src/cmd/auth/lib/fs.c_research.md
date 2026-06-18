# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/lib/fs.c

Defines the global `fs` table for Plan 9 and Securenet key databases. Each entry records mount path, user-facing key description, `who` metadata file, and cached `Biobuf`.

Used by warning and account-management tools to operate on `/mnt/keys` and `/mnt/netkeys` uniformly.
