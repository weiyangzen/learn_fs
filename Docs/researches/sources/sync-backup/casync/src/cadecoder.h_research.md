# sources/sync-backup/casync/src/cadecoder.h

## Purpose

`cadecoder.h` declares the public `CaDecoder` interface. It exposes an opaque decoder type, the event constants returned by `ca_decoder_step()`, configuration hooks for filesystem replay and stream behavior, input/output methods for archive bytes and payload bytes, current-entry metadata accessors, random-access seek controls, replay statistics, digest controls, and hardlink optimization entry points.

The header is the contract used by `casync.c` and any other decoder consumer. It hides the parser state machine and filesystem implementation details in `cadecoder.c` while documenting the caller-driven pull protocol through function names and comments.

## Important APIs, Types, and Constants

`typedef struct CaDecoder CaDecoder;` makes the decoder opaque. Consumers must allocate it with `ca_decoder_new()` and release it with `ca_decoder_unref()`.

The event enum defines stream progress, caller requests, and seek results:

- `CA_DECODER_FINISHED`, `CA_DECODER_STEP`, `CA_DECODER_NEXT_FILE`, `CA_DECODER_DONE_FILE`, and `CA_DECODER_PAYLOAD` describe internal progress and current archive objects.
- `CA_DECODER_REQUEST`, `CA_DECODER_SEEK`, and `CA_DECODER_SKIP` request more input bytes, an absolute input seek, or a relative input skip from the caller.
- `CA_DECODER_FOUND` and `CA_DECODER_NOT_FOUND` report completion or failure of a requested seek.

Configuration APIs include feature flag access/masking, mode booleans for punch holes, reflinks, hardlinks, deletion, payload delivery, immutable-bit undo, UID shifting/ranging, output base fd or boundary fd, base mode for metadata-only/no-filesystem output, and archive size for seekable streams.

Runtime APIs include `ca_decoder_step()`, `ca_decoder_put_data()`, `ca_decoder_put_eof()`, `ca_decoder_get_request_offset()`, `ca_decoder_get_seek_offset()`, `ca_decoder_get_skip_size()`, and `ca_decoder_get_payload()`.

Metadata APIs expose the current path, mode, symlink target, mtime, size, UID/GID, user/group names, device number, payload offset, chattr flags, FAT attributes, xattrs through `CaIterate`, quota project ID, and archive offset.

Digest APIs enable and retrieve archive, payload, and hardlink `CaChunkID` values. `ca_decoder_try_hardlink()` accepts a `CaFileRoot` and path for seed-based hardlink installation during finalization.

## Control Flow Contract

The intended caller loop is event driven. A caller creates a decoder, configures output and replay options, optionally sets archive size, then repeatedly calls `ca_decoder_step()`. On `CA_DECODER_REQUEST`, it asks `ca_decoder_get_request_offset()` for the current absolute input offset and appends bytes with `ca_decoder_put_data()`. On stream end, it calls `ca_decoder_put_eof()`. On `CA_DECODER_SEEK`, it obtains the absolute offset with `ca_decoder_get_seek_offset()`, moves the upstream input source, and feeds bytes from the new position. On `CA_DECODER_SKIP`, it obtains a byte count with `ca_decoder_get_skip_size()` and advances the upstream input source without feeding skipped bytes.

When `CA_DECODER_NEXT_FILE` is returned, current metadata accessors describe the newly parsed object. When `CA_DECODER_PAYLOAD` is returned, `ca_decoder_get_payload()` exposes the current payload span. When `CA_DECODER_DONE_FILE` is returned, payload or hardlink digests may be queried if enabled and valid. When `CA_DECODER_FINISHED` is returned, the archive digest may be queried if enabled.

Seek calls are separate control operations. `ca_decoder_seek_offset()` applies to naked regular/block payloads. `ca_decoder_seek_path()` and `ca_decoder_seek_path_offset()` apply to seekable directory archives with known archive size and goodbye offset information. `ca_decoder_seek_next_sibling()` uses the current path as a starting point.

## State and Persistence Behavior

The header itself has no storage, but it defines ownership and state boundaries. `ca_decoder_set_base_fd()` and `ca_decoder_set_boundary_fd()` transfer practical responsibility for writing under caller-provided fds; the implementation stores these fds and may close owned descriptors during unref. `ca_decoder_set_base_mode()` selects a no-output or metadata-only root mode instead of a filesystem fd.

The API allows persistent filesystem mutation through the decoder: file creation, metadata replay, deletion, hardlinking, reflinking, and hole punching are all controlled by the configuration setters. The current-entry accessors are stateful and meaningful only at the appropriate event positions; most return negative errno-style values such as `-ENODATA`, `-EUNATCH`, or `-EBUSY` when called at the wrong time.

Digest state is opt-in. Enabling digest calculation affects later stepping, and digest getters are constrained by decoder state: archive digest at finished state, payload/hardlink digests at current-file finalization.

## Dependencies and Integration Points

The header includes `cachunkid.h` for digest IDs, `cacommon.h` for shared enums such as `CaIterate`, `calocation.h` and `caorigin.h` for origin/location concepts, and standard integer, boolean, and type headers. It references `CaFileRoot` for hardlink seed roots and `CaOrigin` for input data provenance.

The primary integration point is `casync.c`, which wraps these functions in the higher-level `CaSync` API and CLI behavior. The event constants are also part of the implicit contract with any transport layer that can provide random access, skipping, or remote archive reads.

## Risks and Edge Cases

The enum values are unscoped integer constants. Callers must compare against the named constants and treat negative returns as errors; mixing event values and errno-style errors incorrectly can break restore loops.

The API requires strict state discipline. Feeding bytes after EOF, requesting payload data outside `CA_DECODER_PAYLOAD`, reading digests in the wrong state, seeking before archive size is known, or setting configuration after parsing has started can return errors or produce stale digest state.

File-descriptor ownership is not fully inferable from the declarations alone, so callers must follow implementation expectations and avoid reusing fds in surprising ways after handing them to the decoder. Boundary and base fd modes are mutually constrained.

The header exposes many filesystem replay toggles. Tests and callers need to understand that disabling payload delivery does not necessarily disable filesystem writes, and disabling replay feature bits via the mask changes which archived metadata is honored.

## Test Signals

Compile tests should include this header from C and C++-style consumers if applicable, verify all dependent headers resolve, and ensure the opaque type can be allocated and released without exposing internals.

API contract tests should assert that invalid `NULL` arguments produce negative errors, configuration setters reject invalid states, event returns are handled distinctly from errno values, and metadata/digest accessors return `-ENODATA` or `-EBUSY` outside their legal event windows.

Integration tests should exercise a full caller loop using only declarations in this header: configure decoder, feed bytes on requests, perform skip/seek handling, read payloads and metadata at event boundaries, and retrieve digests at the documented terminal states.
