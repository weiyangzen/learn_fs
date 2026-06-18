# sources/user-network-fs/go-fuse/benchmark/bulkstat/main.go

Purpose: external helper that repeatedly stats path lists in parallel so benchmark timing can focus on FUSE server work rather than in-process benchmark overhead.

Important APIs/functions: `BulkStat(parallelism, files)` starts worker goroutines consuming a buffered channel of paths and calling `os.Lstat`; `ReadLines` streams a file list with `bufio.Reader.ReadLine`; `main` parses `-N`, `-cpu`, `-prefix`, `-quiet`, prefixes paths, and loops until N stat operations are performed.

Control flow/state: workers terminate on zero-value string after channel close. Since the channel is buffered to `len(files)`, enqueueing does not block for normal inputs.

Dependencies/integration: built as `bulkstat.bin` and invoked by `stat_test.go`. Risks: `ReadLine` can truncate very long lines, `log.Fatal` exits the process on the first stat error, and an empty filename sentinel means blank path entries are unsupported. Test signal is benchmark success against generated path lists.
