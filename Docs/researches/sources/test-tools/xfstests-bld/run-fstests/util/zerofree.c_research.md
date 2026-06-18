# sources/test-tools/xfstests-bld/run-fstests/util/zerofree.c

- Purpose: ext filesystem free-block zeroing utility; it opens an ext2-family filesystem image/device and writes zeros to unused blocks so sparse/compressed appliance images shrink better. The file is 165 lines/3531 bytes and is researched as source path `sources/test-tools/xfstests-bld/run-fstests/util/zerofree.c`.
- Important APIs/types/functions: C program using ext2fs library calls, block bitmap iteration, file/device open/write paths, and command-line arguments for target filesystem/device handling.
- Control flow: opens the ext filesystem, walks free block metadata, writes zero-filled buffers to free blocks, reports progress/errors, and closes filesystem resources.
- State and persistence: mutates the underlying filesystem image/device by zeroing unused blocks; intended state change is data-neutral for allocated files but affects raw free-space contents and image compressibility.
- Dependencies/integration: depends on libext2fs/e2fsprogs headers and is useful during appliance image preparation before export/compression.
- Risks and test signals: unsafe on mounted or unsupported filesystems and dangerous on wrong devices; validate on disposable ext images with fsck before/after and image-size comparison.
