# sources/user-network-fs/rclone/lib/readers/readfill.go

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/readers/readfill.go -->
## sources/user-network-fs/rclone/lib/readers/readfill.go

Purpose: reads as much as possible into a buffer until the buffer is full or the reader returns an error, without requiring an exact fill like `io.ReadFull`.

Important APIs and control flow: `ReadFill(r, buf)` loops while `n < len(buf)` and `err == nil`, reading into `buf[n:]` and accumulating bytes. It returns the final count and the last error, including `io.EOF` if EOF stopped the loop before the buffer filled.

State, dependencies, and integration: stateless helper depending only on `io`. It integrates with callers that want a best-effort block read and need to retain partial bytes plus terminal error.

Risks and test signals: a reader returning `(0, nil)` repeatedly would cause an infinite loop. This is the same class of misuse many read loops must guard against, but no guard exists here. Tests cover empty, partial, and full buffer reads with a one-byte-at-a-time reader.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/readers/readfill.go -->
