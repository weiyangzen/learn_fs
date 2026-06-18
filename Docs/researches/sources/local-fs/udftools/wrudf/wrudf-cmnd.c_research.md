# File Research: sources/local-fs/udftools/wrudf/wrudf-cmnd.c

## Purpose

`wrudf-cmnd.c` implements the interactive shell commands for modifying a UDF volume: copying files/directories from the host filesystem, removing entries, creating/removing directories, changing the current UDF or host directory, and listing UDF or host contents. It also owns most in-memory `Directory` loading and dirty directory serialization.

## Copying Files

`copyFile()` imports one regular host file into a UDF directory:

- Opens the source file and prompts for overwrite if the destination FID exists.
- Creates a new FID and File Entry.
- Copies uid, gid, POSIX mode bits into UDF permission bits, setuid/setgid flags, size, and timestamps.
- For CD-R, uses long allocation descriptors, reserves a virtual file-entry VAT entry, writes the file entry first, then file data in variable packet chunks, syncs, and verifies with `verifyCDR()`.
- For CD-RW, allocates a short extent for the file entry, allocates short extents for file data from the space bitmap, writes the file entry and blocks through the packet-cache layer.
- Inserts the new FID into the destination directory and increments the LVID implementation-use file count.

CD-R file data descriptors point into the physical writable partition while the file entry itself is referenced through the virtual partition/VAT.

## Copying Directories

`copyDirectory()` recursively imports host directory contents when `OPT_RECURSIVE` is set. It skips `.` and `..`, uses `lstat()` so symlinks are not followed, creates or reuses destination directories, recursively imports child directories, and imports regular files with `copyFile()`.

It changes the process working directory while traversing and then changes back upward; `cpCommand()` later restores `hdWorkingDir`.

## Removing Entries

`deleteDirectory()` recursively deletes directory contents by reading the child directory, walking FIDs, deleting regular children with `deleteFID()`, recursively deleting directories, and deleting the directory FID when empty.

`rmCommand()` deletes files directly and deletes directories only with `OPT_RECURSIVE`. `rmdirCommand()` requires exactly one directory argument, verifies it is empty, rejects root directory removal, and then deletes the directory FID.

## Directory Loading

`readDirectory()` materializes a UDF directory into a `Directory` object:

- Reuses the single cached child directory under the parent when it already matches the requested ICB.
- Flushes a dirty cached directory before replacing it.
- Reads the directory file entry through `readTaggedBlock()`.
- If allocation descriptors are embedded in the ICB, copies FID bytes out of the file entry into `dir->data`.
- Otherwise reads directory data through `readExtents()`.
- On CD-RW, frees the old directory data extents after loading because rewritten directories will get fresh extents.

The design keeps at most one active child chain from root to current directory, rather than a general directory cache.

## Directory Serialization

`updateDirectory()` recursively flushes dirty child directories first, then serializes the current dirty directory:

- If all FIDs fit inside the file entry, it switches to `ICBTAG_FLAG_AD_IN_ICB`, embeds directory data, and updates FID tag locations to the directory ICB location.
- If external allocation is needed on CD-R, it uses long descriptors at the next append location and sets FID tag locations to future physical directory-data blocks.
- If external allocation is needed on CD-RW, it allocates short extents, builds a block list for tag-location assignment, and writes directory data through `writeExtents()`.
- It recomputes descriptor CRC lengths and checksums.
- It writes the directory file entry in place for CD-RW or appends a replacement file entry and updates VAT for CD-R.

## Directory Creation

`makeDir()` creates a child directory with:

- A parent/back-reference FID with `FID_FILE_CHAR_DIRECTORY | FID_FILE_CHAR_PARENT`.
- A directory file entry with embedded allocation descriptors.
- A forward FID inserted into the parent.
- CD-R virtual ICB allocation through `newVATentry()` or CD-RW physical file-entry allocation through `getExtents()`.
- Parent file-link-count increment and LVID directory-count increment.

It constructs or reuses the parent's cached child `Directory` structure and marks it dirty.

## Path Analysis And Commands

`analyzeDest()` resolves slash-separated UDF paths against `curDir`, supports absolute paths, `.`, `..`, trailing slash removal, and returns an `enum RV` state describing whether the final component is an existing directory, existing file, deleted entry, missing entry, or invalid path.

Command handlers:

- `cpCommand()` parses destination state, handles deleted/overwrite cases, imports each source argument, and supports recursive directory copy.
- `mkdirCommand()` creates one directory and changes into it.
- `cdcCommand()` changes current UDF directory by relying on `analyzeDest()`.
- `lscCommand()` lists UDF directory entries with type, uid/gid permissions, link count, information length, and decoded filename.
- `cdhCommand()` changes host working directory and updates `hdWorkingDir`.
- `lshCommand()` shells out to `ls -l` plus an optional argument.

## Notable Details

Several directory iteration loops use `fid` in the increment expression before assigning it inside the loop body; the intended pattern works after the first body assignment but is fragile C and easy to misread.

`copyFile()` treats `open()` returning file descriptor `0` as failure, although `0` is a valid descriptor. It should check `< 0`; as written, copying can fail incorrectly if stdin is closed.

`lshCommand()` builds a shell command with `strncat()` and `system()`, so host-path listing arguments are shell-interpreted.
