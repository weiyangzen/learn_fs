# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/TarExtractor.java

## Purpose
`TarExtractor` extracts tar archive contents into a staging directory with parallel file writes, then replaces the target output directory.

## Important APIs, Types, And Functions
The constructor accepts thread-pool size and thread-name prefix. Public lifecycle methods are `start`, `extractTar(InputStream,Path)`, and `stop`. Private helpers `readEntryData` and `writeFile` buffer tar entry bytes and write them to disk.

## Control Flow
`start()` creates a fixed executor once. `extractTar()` creates a `.staging_<uuid>` sibling directory, sequentially reads tar entries, buffers each file entry into memory, submits write tasks, waits for all futures, deletes an existing output directory, then attempts an atomic move from staging to output. `stop()` shuts down the executor and awaits termination.

## State And Persistence
Runtime state is an executor guarded by `AtomicBoolean`. Persistent effects are staging directory creation, extracted files, deletion of existing output, and final directory replacement.

## Dependencies And Integration Points
It depends on Guava thread factories, Apache Commons Compress tar streams, Commons IO `FileUtils`, and `ReconConstants.STAGING`. It is suited for OM/SCM snapshot extraction flows.

## Risks
Calling `extractTar` before `start` causes a null executor. Each file is fully buffered in memory and casts entry size to int, which is unsafe for very large entries. If atomic move fails, it only logs a warning and leaves staging/output state ambiguous. Tar entry names are written directly, so path traversal protection is not explicit.

## Test Signals
Tests should cover lifecycle ordering, directory and file extraction, existing output replacement, large file behavior, failed write propagation through futures, interrupted shutdown, atomic move fallback, and malicious entry names.
