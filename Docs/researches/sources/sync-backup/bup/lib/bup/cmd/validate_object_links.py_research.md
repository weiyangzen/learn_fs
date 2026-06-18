# sources/sync-backup/bup/lib/bup/cmd/validate_object_links.py

## Purpose
`validate_object_links.py` scans pack contents and reports missing object links from commits and trees to their referenced parents, trees, and child entries.

## APIs and Control Flow
`obj_type_and_data_ofs` parses Git pack object header kind and compressed-data offset. `Pack` opens a pack associated with an idx, iterates non-blob objects by offset order, decompresses whole commit/tree/tag objects directly or resolves deltas through `catpipe`, and yields `(oid, type, data)`. `main(argv)` rejects args, checks the repo, counts objects, iterates every idx and pack, derives referenced SHA lists from `tree_iter` or parsed commits, and checks existence in `PackIdxList`.

## State, Dependencies, Integration, Risks, Tests
It is read-only and returns `EXIT_FALSE` when missing links are found. Dependencies include pack file format, `git.tree_iter`, `git.parse_commit`, `PackIdxList`, `pairwise`, and zlib. Risks include assuming pack version 2 and 5-byte headers are enough for 4GiB objects, skipping tag objects, private idx methods, and object count zero division in progress. Test signals include missing child detection, delta object handling, tag warning, no-argument fatal, pack header parsing, and progress across multiple idx files.
