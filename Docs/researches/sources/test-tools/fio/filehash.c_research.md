# sources/test-tools/fio/filehash.c

## Purpose
`filehash.c` maintains a global hash table of fio files by filename and a bloom filter for quick existence-style checks. It prevents duplicate file entries from being added silently and gives callers lookup/removal helpers.

## Important APIs, Types, And Functions
The hash table has 512 buckets (`HASH_BUCKETS`) indexed by Jenkins hash masked with `HASH_MASK`. Global state includes `file_hash`, `hash_lock`, and `file_bloom`. Public APIs are `file_hash_init`, `file_hash_exit`, `lookup_file_hash`, `add_file_hash`, `remove_file_hash`, explicit lock/unlock helpers, and `file_bloom_exists`.

## Control Flow
`file_hash_init()` allocates buckets with `smalloc`, initializes each list, creates a semaphore, and allocates the bloom filter. `add_file_hash()` initializes the file's hash link, locks the table, searches for an existing filename, and either returns the alias or inserts the file and sets its `hashed` flag. `lookup_file_hash()` locks around a bucket scan. `remove_file_hash()` deletes the entry if its flag says it is hashed. `file_hash_exit()` checks for remaining entries, frees table/semaphore/bloom, and clears globals.

## State And Persistence
The table and bloom filter are process-global volatile state. The bloom filter may retain names until exit and can produce false positives. Each `fio_file` records membership through `FIO_FILE_hashed` and `hash_list`.

## Dependencies And Integration Points
The implementation depends on fio lists, semaphores, Jenkins hash, smalloc, bloom filter code, logging, and `fio_file` flag helpers from `file.h`.

## Risks
`file_hash_init()` does not check allocation failures for the hash table, semaphore, or bloom filter before use. `file_bloom_exists()` assumes `file_bloom` is initialized. The bloom filter cannot remove names. `file_hash_exit()` only logs if entries remain, then frees the table anyway, so leaked file membership is diagnostic rather than fatal.

## Test Signals
Unit tests should cover insert, duplicate alias return, lookup, removal, idempotent removal of unhashed files, bloom set/query behavior, lock/unlock helpers before/after init, and exit with non-empty hash diagnostic.
