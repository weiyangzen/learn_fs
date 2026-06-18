# sources/test-tools/stress-ng/stress-mincore.c

Purpose: `stress-mincore.c` exercises the `mincore` syscall over mapped, file-backed, unmapped, random/linear, and deliberately invalid arguments. It validates expected success/failure behavior and measures nanoseconds per successful mapped-page `mincore` call.

Important APIs/types/functions: `stress_mincore_file` creates a temporary file, unlinks it immediately, fallocates one page, and returns the fd for file-backed mapping. `stress_mincore_expect` compares return values and errno against expectations while ignoring `ENOSYS`. `stress_mincore` owns the test loop and cleanup.

Control flow: the stressor reads `--mincore-random`, maps one anonymous page, creates/maps one file-backed page if possible, and creates then unmaps a page to preserve an unmapped address. After sync, it loops 100 address probes per bogo iteration. It calls `shim_mincore` on the moving address, on the resident anonymous page, on the file-backed page after writes and optional `msync`, on the unmapped page, and on invalid combinations such as zero length, misaligned address, NULL vec, invalid vector address, NULL address, and NULL/zero arguments. Linear mode increments the probe address by page size; random mode derives page-aligned addresses from MWC RNG and avoids repeating the same address.

State and persistence behavior: persistent filesystem state is limited to a temp directory and unlinked temp file fd, removed during cleanup. Runtime memory state includes anonymous/file mappings and one unmapped address. Metrics are local duration/count values reported as harmonic mean.

Dependencies and integration points: the file uses stress-ng temp-file helpers, `shim_mincore`, `shim_fallocate`, `shim_msync`, memory naming, metrics, and option metadata. It registers as `CLASS_OS | CLASS_MEMORY` with `VERIFY_ALWAYS`; unsupported builds register an unimplemented reason for missing `mincore`.

Risks: errno behavior for invalid `mincore` arguments varies across kernels/libc, and the code explicitly tolerates some alternatives such as `ENOMEM` for NULL/zero arguments. Random address probing can hit mapped regions and should not be treated as a hard failure except unexpected errno. Temp-file setup failure only disables file-backed coverage, not the whole stressor.

Test signals: run `stress-ng --mincore 1 --mincore-ops 1 --verify`, repeat with `--mincore-random`, and test on a system without `mincore` support if possible to verify `EXIT_NOT_IMPLEMENTED`. Metrics should include “nanosecs per mincore call”.
