# sources/security-integrity/cryfs/old-cpp/src/stats/main.cpp

Purpose: command-line `cryfs-stats` tool that opens an encrypted CryFS basedir read-only, prints configuration, finds all on-disk blocks, subtracts blocks reachable from filesystem blobs, and reports unaccounted block depths.

Important APIs/types/functions: `makeBlobStore`, `makeBlockStore`, `AccumulateBlockIds`, `ProgressBar`, `getKnownBlobIds`, `getKnownBlockIds`, `getAllBlockIds`, `printConfig`, and `main`.

Control flow: validates one argument, prompts for password, loads config read-only, checks format compatibility, enumerates all block IDs, recursively traverses reachable blobs and their blocks, erases accounted IDs from a set, then prints orphan/unaccounted leaf versus inner node counts.

State and persistence behavior: uses local state directory integrity data and opens Rust bridge stores in read-only locking/integrity/encrypted mode. It does not mutate the filesystem, but it may read integrity metadata and emits warnings on integrity violations.

Dependencies and integration points: integrates `CryConfigLoader`, password-based key provider with SCrypt, Rust block/blob-store bridge factories, `LocalStateDir`, `IOStreamConsole`, and traversal helpers.

Risks and test signals: assertions assume reachable references always exist on disk. Password prompting and full block traversal make this a manual diagnostic tool; no direct automated tests in this subset cover it.
