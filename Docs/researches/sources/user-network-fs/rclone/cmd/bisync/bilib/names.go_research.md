# sources/user-network-fs/rclone/cmd/bisync/bilib/names.go

Purpose: small set utilities for bisync filename tracking plus alias mapping for normalized/case-equivalent names. `Names` is a map-backed set; `AliasMap` stores bidirectional equivalence pairs.

APIs: `ToNames`, `Add`, `Has`, `NotEmpty`, `ToList`, `Save`, `SaveList`, `AliasMap.Add`, and `AliasMap.Alias`. `SaveList` writes sorted, quoted names with secure `0600` permissions. State changes are local list-file writes. Dependencies are bytes, sort, strconv quoting, and OS writes. Risks include map value type `any` being larger than needed, write not atomic, and alias map supporting only one alternate per name. Test signal is indirect through bisync list/state tests.
