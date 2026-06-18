<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-annex/doc/special_remotes/external/git-annex-remote-ipfs -->
# sources/sync-backup/git-annex/doc/special_remotes/external/git-annex-remote-ipfs

Purpose: experimental external special remote that stores git-annex content in IPFS and tracks IPFS addresses as git-annex URLs.

Important functions: `isipfsurl` recognizes `ipfs:` URLs, `urltoaddress` strips the prefix, `addresstourl` adds it, `getvalue` parses protocol `VALUE` responses, and `getaddrs` asks git-annex for all URLs for a key and writes matching IPFS URLs to a temp file.

Control flow: emits `VERSION 2`. `INITREMOTE` and `PREPARE` always succeed. `CLAIMURL` accepts only `ipfs:` URLs. `CHECKURL` returns `CHECKURL-CONTENTS UNKNOWN <address>`. `TRANSFER STORE` runs `ipfs add -q`, then emits `SETURIPRESENT` and transfer success. `TRANSFER RETRIEVE` retrieves known IPFS URLs with `GETURLS`, selects the first, and runs `ipfs get --output="$file"`. `CHECKPRESENT` always reports failure, and `REMOVE` reports failure because IPFS content cannot be removed remotely.

State and persistence: no local configuration is persisted by the script. Durable availability is delegated to the user's IPFS node/network and git-annex URL records.

Dependencies and integration points: POSIX shell, `ipfs`, `egrep`, `sed`, `mktemp`, `head`, and git-annex external special remote protocol.

Risks: presence checking is intentionally weak and always says the key is not present. Retrieval picks only the first known IPFS URL. `ipfs get --output="$file"` behavior depends on IPFS client semantics and may create directories for some CIDs. No pinning or garbage-collection policy is managed here.

Test signals: store a file and confirm `SETURIPRESENT`, retrieve from recorded `ipfs:` URL, reject non-IPFS URLs, handle absent `ipfs`, and verify remove/presence responses match the protocol.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-annex/doc/special_remotes/external/git-annex-remote-ipfs -->
