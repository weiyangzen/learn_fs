# File Research: sources/os/plan9/9front/sys/src/cmd/aux/rdwr.c

`rdwr` is an interactive read/write exerciser for a file opened `ORDWR`. With `-w`, it reads and prints the current contents first. Then it repeatedly prompts, writes each input line minus its trailing newline at offset 0, seeks back, reads up to 8192 bytes, and prints the result.

It is useful for testing device files and control interfaces where writes change immediately readable state. Errors are printed but the loop continues unless open fails.
