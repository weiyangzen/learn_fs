# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/score.c

`score.c` defines the global zero score and helper functions for Venti SHA1 scores. `scoremem()` hashes a memory buffer into a score, and `strscore()` parses a hex score string into 20 bytes.

`needzeroscore()` is a link anchor for environments that otherwise omit the object defining `zeroscore`. The parser accepts upper and lower hex and requires exact string termination after `2*VtScoreSize` digits.
