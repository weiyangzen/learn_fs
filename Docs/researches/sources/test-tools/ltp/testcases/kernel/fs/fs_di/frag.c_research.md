# sources/test-tools/ltp/testcases/kernel/fs/fs_di/frag.c

Purpose: creates two fragmented files from one input data file by repeatedly appending 1 KiB chunks, fsyncing, and closing both output files after each chunk.

Important APIs/types/functions: global `FILE *` handles, `main`, `fopen`, `fread`, `fwrite`, `fileno`, `fsync`, `fclose`, `strcpy`, and `strcat`.

Control flow: expects input file and output directory arguments, opens the data file, constructs `frag1` and `frag2` paths, repeatedly opens both outputs with `a+`, reads up to 1024 bytes, writes the same bytes to both outputs, fsyncs their descriptors, closes them, and stops at a short read.

State/persistence behavior: appends to `<dir>/frag1` and `<dir>/frag2`; repeated open/fsync/close cycles intentionally encourage fragmented allocation on the target filesystem.

Dependencies/integration: called by `fs_di` when the `-S` disk-size option enables fragmented-file validation.

Risks/test signals: fixed 100-byte path buffers can overflow for long directories. It treats `fread` byte count as signed even though `fread` returns `size_t`. Success is exit 0 and later `cmp` equality with the source data file.
