<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_pointer.go -->
# sources/sync-backup/git-lfs/commands/command_pointer.go

Purpose: implements `git lfs pointer`, generating LFS pointer text for a file, validating pointer files, and comparing generated pointers with existing pointer input.

Important APIs/types/functions: globals `pointerFile`, `pointerCompare`, `pointerStdin`, `pointerCheck`, `pointerStrict`, `pointerNoStrict`, `pointerNoExtensions`; `pointerCommand` and `pointerReader`; `lfs.DecodePointer`, `lfs.EncodePointer`, `lfs.NewPointer`, `git.HashObject`, and `lfs.GitFilter.Clean`.

Control flow: `--check` validates exactly one input source, rejects incompatible strict flags, decodes the pointer, and exits 1 for invalid or 2 for noncanonical strict mode. Generation opens `--file`, either hashes directly for plain pointer/no repo or cleans through GitFilter to honor extensions, prints pointer to stdout and diagnostics to stderr, optionally hashes the pointer blob. Comparison reads `--pointer` or stdin, decodes and prints it, hashes it, and exits nonzero if blob OIDs differ.

State and persistence behavior: mostly read-only, but generation through `GitFilter.Clean` can invoke extension clean logic and may create temporary cleaned state depending on implementation. Output is split between stdout pointer text and stderr diagnostics.

Dependencies/integration points: integrates LFS pointer encoding/decoding, optional configured extensions, Git blob hashing, stdin validation, and repository detection.

Risks and test signals: risks include clean result teardown not explicit in this command, confusing stdout/stderr split for scripts, extension-driven pointer mismatch, and strict/no-strict flag interaction only enforced in check mode. Test signals include plain pointer generation, extension warning, invalid pointer check exit 1, noncanonical strict exit 2, file-vs-pointer comparison match/mismatch, stdin comparison, and no-op error.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_pointer.go -->
