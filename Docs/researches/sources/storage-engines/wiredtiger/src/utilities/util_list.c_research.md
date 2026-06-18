## sources/storage-engines/wiredtiger/src/utilities/util_list.c

Purpose: implements `wt list`, printing metadata object names and optionally full config and checkpoint details.

Important APIs/types/functions: `util_list` parses `-c`, `-f output`, `-v`, and optional URI. `list_print` scans `WT_METADATA_URI`. `list_print_checkpoint` reads checkpoint lists with `__wt_metadata_get_ckptlist`, obtains allocation size via `list_init_block`, decodes checkpoint addresses with `__wt_block_ckpt_decode`, and prints sizes via `list_print_size`.

Control flow: command normalizes optional URI through `util_uri`, opens optional output, and calls `list_print`. `list_print` scans metadata in key order, filters by URI prefix when supplied, suppresses system metadata/history store unless verbose/checkpoint output is requested, prints keys, and optionally prints checkpoint and config details. Missing requested URI returns a not-found message and exit code `1`. Checkpoint printing iterates checkpoints, prints name/time/size, decodes raw block checkpoint fields when available, and ignores decode errors after reporting them.

State and persistence behavior: read-only metadata inspection. It writes output to stdout or a user file and propagates close errors. It allocates/frees metadata config strings and checkpoint lists.

Dependencies and integration points: uses metadata cursor APIs, extension API metadata/config parser functions, block checkpoint decoding, WiredTiger size constants, utility output-file helpers, and `util_uri`. It depends on metadata config containing `allocation_size` for accurate checkpoint address decoding.

Risks: URI filtering is prefix-based, so a requested prefix can match multiple related metadata entries. Verbose/checkpoint modes expose internal system entries otherwise hidden. `ctime` output is locale/timezone sensitive. Checkpoint decode uses a dummy `WT_BLOCK` initialized mainly with allocation size, which the source itself notes as a kludge.

Test signals: listing empty/new homes, normal object listing excluding metadata/history store, verbose full schema output, checkpoint output for objects with multiple checkpoints, output redirection and close failure, URI filter not found, system entry visibility under `-v`/`-c`, and damaged checkpoint address handling that reports but continues.
