# File Research: sources/local-fs/mtd-utils/tests/fs-tests/stress/atoms/rmdir00.c

## Purpose
Repeated create-and-remove directory tree stress test.

## Key Elements
Creates `rmdir00_test_dir_<pid>`, repeatedly clears it, fills it with random empty subdirectories and small files until size threshold or `ENOSPC`, optionally sleeps, then removes everything and the top directory.

## Dependencies
Uses shared entry create/remove and cleanup helpers.

## Behavior/Risks
`-z0` fills until no space remains. Directory cleanup depends on recursive deletion helper and `dirent.d_type`.
