# sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/utils/targetsutils.py

Purpose: manages ntlmrelayx target selection, target exhaustion, identity-specific matching, target-file reloads, and `all://` expansion across protocol clients.

Important APIs and control flow: `TargetsProcessor.__init__()` loads a single target or file, optionally randomizes, then calls `reloadTargets(full_reload=True)`. `processTarget()` defaults bare hosts to SMB, parses URI targets, and expands `ALL...` into one URL per registered protocol. `readTargets()` ignores blank/comment lines. `reloadTargets()` rebuilds `generalCandidates` and `namedCandidates` excluding finished/failed attacks. `registerTarget()` records finished or failed attempts, converting general targets into identity-qualified URLs when a username is known. `getTarget()` tries explicit username matches, identity-specific general targets not already finished/failed, one-shot behavior for `multiRelay=False`, then reloads remaining candidates. `TargetsFileWatcher` polls mtime and refreshes.

State and persistence: keeps `originalTargets`, `finishedAttacks`, `failedAttacks`, candidate lists, and file mtime in memory. It reads target files but writes no files.

Dependencies and integration: depends on `urlparse`, `random`, `os`, `time`, `Thread`, and `impacket.LOG`. Relay servers call `getTarget()` and `registerTarget()` to coordinate multirelay progress.

Risks and test signals: candidate state is not locked for concurrent handlers. `getTarget()` contains a stray `print(self.failedAttacks)`. URL username/domain comparison is case-normalized inconsistently. Tests should cover bare host defaulting, URI parsing, ALL expansion, file reload, randomization, named identity matching with and without domain, duplicate finished/failed suppression, multiRelay disabled semantics, and watcher refresh.
