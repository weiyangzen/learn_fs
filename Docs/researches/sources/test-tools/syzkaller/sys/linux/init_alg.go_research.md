## sources/test-tools/syzkaller/sys/linux/init_alg.go

Purpose: Linux AF_ALG special generation for `sockaddr_alg` and algorithm-name structs.

Important APIs/types/functions: `generateSockaddrAlg`, `generateAlgName`, `generateAlgAeadName`, `generateAlgHashName`, `generateAlgSkcipherhName`, `generateAlgNameStruct`, `generateAlgName`, `generateAlg`, `generateAlgImpl`, `fixedSizeData`, `algType`, `algDesc`, algorithm kind constants, `allTypes`, and `allAlgs`.

Control flow: `generateSockaddrAlg` generates the family, mostly zeroes feature/mask, randomly selects an algorithm type/name, pads or truncates fixed-size fields, and returns a struct arg. Name-specific functions generate fixed-size name structs for selected algorithm families. Recursive templates such as `authenc(hash,skcipher)` are built by `generateAlgImpl`.

State and persistence: static in-memory algorithm catalog. Generation returns new `prog.Arg` objects and no persistent writes.

Dependencies/integration: registered as Linux `target.SpecialTypes` in `init.go`; uses `prog.Gen` for random and regular field generation.

Risks: algorithm catalog can drift from kernel crypto availability. Recursive templates are bounded by catalog structure, not explicit recursion depth. Fixed-size truncation can cut generated names, which may be intentional for fuzzing but affects validity.

Test signals: indirectly covered by `TestSpecialStructs`, generation, mutation, and Linux target tests.
