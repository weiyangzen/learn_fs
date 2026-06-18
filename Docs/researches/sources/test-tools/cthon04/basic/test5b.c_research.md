# sources/test-tools/cthon04/basic/test5b.c

Purpose: read-focused large-file test that assumes the target file already exists.

Important APIs/types/functions: parses -h, -t, -f, -n plus size/count/fname. Uses mtestdir(), open(O_RDONLY), read(), optional mmap/msync/munmap, unlink(), and timing helpers.

Control flow: moves into the existing test directory, repeatedly opens and reads size bytes from bigfile, closes each pass, prints read throughput, then unlinks the file.

State and persistence: consumes and removes the bigfile, usually one produced by test5a. It does not create fallback data.

Dependencies and integration points: paired with test5a in harness sequencing; DOS/Win32 adds O_BINARY to reads.

Risks: -n is parsed but ignored because the program always calls mtestdir(); missing or wrong-size bigfile causes read failure; content is not validated.

Test signals: successful full-length reads and final unlink lead to complete(); open/read/unlink failures are fatal.
