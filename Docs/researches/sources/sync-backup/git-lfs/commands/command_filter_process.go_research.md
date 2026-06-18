<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_filter_process.go -->
# sources/sync-backup/git-lfs/commands/command_filter_process.go

Purpose: implements Git's long-running `filter-process` protocol for clean, smudge, delayed smudge, and `list_available_blobs` interactions.

Important APIs/types/functions: constants `cleanFilterBufferCapacity`, `smudgeFilterBufferCapacity`; global `filterSmudgeSkip`; `filterCommand`, `infiniteTransferBuffer`, `incomingOrCached`, `readAvailable`, `pathnames`, `statusFromErr`, and `delayedStatusFromErr`. It uses `git.FilterProcessScanner`, `pktline.PktlineWriter`, `lfs.GitFilter`, `tq.TransferQueue`, and shared `clean`/`smudge` helpers.

Control flow: requires stdin, sets up repo/hooks, negotiates capabilities, detects `delay`, builds skip/filter state, then loops over Git filter requests. `clean` writes pointer output; `smudge` either initializes a delayed download queue and queues missing objects when `can-delay=1`, or smudges immediately using cached pointer fallback; `list_available_blobs` starts queue drain and returns ready pathnames until completion. Malformed pointer and Windows large-file warnings are accumulated and printed after the scan.

State and persistence behavior: long-lived process holds a transfer queue, delayed pathname-to-pointer map, malformed path lists, and channel buffer goroutine. It downloads into the LFS object store, writes blobs/pointers over pktline stdout, and installs hooks opportunistically.

Dependencies/integration points: tightly integrates with Git filter protocol capabilities, pkt-line framing, transfer queue batch behavior, auto remote detection from treeish, include/exclude filters, and shared clean/smudge semantics.

Risks and test signals: risks include nil `closeOnce` if `list_available_blobs` arrives without delayed smudge setup, protocol status ordering, channel close/race behavior in delayed queue buffering, path cache for `can-delay=0` follow-up requests, and large warning behavior. Test signals include Git checkout with filter-process, clean requests, immediate smudge, delayed smudge with repeated list calls, skip smudge, malformed pointers, and queue errors mapped to protocol statuses.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_filter_process.go -->
