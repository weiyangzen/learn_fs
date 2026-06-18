# sources/sync-backup/bup/lib/bup/cmd/join.py

## Purpose
`join.py` reconstructs file content from bup refs or object hashes by streaming joined blob/tree content to stdout or a named output file.

## APIs and Control Flow
`main(argv)` resolves an optional remote repository, reads refs from positional arguments or stdin lines, opens `repo_for_location`, and opens `-o` output if provided. For each ref it calls `src.join(ref)` and writes each returned blob to the output stream. `KeyError` is logged and returns failure.

## State, Dependencies, Integration, Risks, Tests
The command is read-only against the repository but can overwrite the output file path. Dependencies include `repo.join`, `linereader`, `byte_stream`, and `main_repo_location`. It integrates with split/save data retrieval and remote repository access. Risks include partial output before a later ref fails, missing object/ref errors surfacing as `KeyError`, and no explicit append/overwrite controls for `-o`. Test signals include stdin ref mode, remote repository opening, binary output correctness, output file handling, and failure after flushing partial data.
