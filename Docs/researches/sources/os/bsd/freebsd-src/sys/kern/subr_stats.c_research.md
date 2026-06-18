# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_stats.c

## Purpose
Implements the FreeBSD `stats(9)` version-1 stats blob/template subsystem. It provides compact in-memory templates and per-entity stats blobs for values of interest (VOIs), supporting numeric aggregations, histograms, t-digests, string/JSON rendering, snapshot/reset, template lookup, and kernel sysctl exposure.

## Main Data Model
- `struct statsblobv1` is the serialized/cloneable blob header plus packed `struct voi[]`, `struct voistat[]`, and voistatdata regions.
- `struct voi` describes one value of interest: ID, data type, stats offset, maximum stat slot, and flags such as `VOI_REQSTATE`.
- `struct voistat` describes a stat attached to a VOI: stat type, data type, data offset/size, validity flag, and capped error count.
- `struct statsblobv1_tpl` combines template metadata (`struct metablob`) and a template stats blob.
- Data type metadata is centralized in `vsd_dtype2name`, `vsd_dtype2size`, `vsd_compoundtype`, and `numeric_limits`.

## Template Lifecycle
- `stats_v1_tpl_alloc()` creates a named template, initializes ABI/endian/size fields, stores it in global `tpllist`, and computes a stable template hash.
- `stats_v1_tpl_add_voistats()` adds a new VOI and its stats to a template. It supports adding new VOIs but explicitly rejects expanding an existing VOI with `EOPNOTSUPP`.
- `stats_v1_blob_expand()` grows and reshuffles the blob layout, preserving offsets and initializing newly inserted VOI/stat/data regions.
- `stats_tpl_update_hash()` hashes the template name, VOI names, and blob bytes.
- `stats_tpl_fetch()`, `stats_tpl_fetch_allocid()`, and `stats_tpl_id2name()` provide lookup by slot, name, and/or hash.

## Blob Lifecycle
- `stats_v1_blob_alloc()` allocates a stats blob sized from a template and initializes it.
- `stats_v1_blob_init()`/`stats_v1_blob_init_locked()` copy template bytes into an instance, set creation/reset timestamps, and stamp the template hash.
- `stats_v1_blob_clone()` copies a blob to kernel or user memory, preserving destination `maxsz` semantics and returning `EOVERFLOW` if the destination cannot hold the full source.
- `stats_v1_blob_snapshot()` clones a blob, optionally resets the source stats, and calls the currently stubbed `stats_v1_blob_finalise()`.
- `stats_v1_blob_destroy()` frees blob storage.
- `stats_v1_voistat_fetch_dptr()` returns the data pointer, type, and size for a VOI/stat pair.

## Stat Helpers
- `stats_vss_numeric_hlpr()` initializes SUM/MIN/MAX numeric stats for integer and fixed-point Q types.
- `stats_vss_hist_hlpr()` builds histogram initial values using linear, exponential, linear-exponential, or user-specified buckets; it supports count/range/value histogram forms and optional infinite bounds for compatible histogram types.
- `stats_vss_tdgst_hlpr()` initializes 32-bit or 64-bit t-digest centroid storage using the array-backed red-black (`ARB`) tree.
- `stats_vss_hlpr_init()` and `stats_vss_hlpr_cleanup()` run and clean helper-provided initial values.

## Update Behavior
- `stats_v1_voi_update()` validates blob ABI, VOI ID/type, and relative-update state, then updates all configured stats for the VOI.
- Relative updates use the hidden `VS_STYPE_VOISTATE` stat to accumulate the supplied delta into the previous value before updating stats.
- Numeric updates are split into:
  - `stats_v1_voi_update_sum()`
  - `stats_v1_voi_update_min()`
  - `stats_v1_voi_update_max()`
- Histogram updates search buckets from the end and increment the matching bucket or out-of-bounds count.
- T-digest updates convert the VOI value to the centroid precision, merge into an eligible centroid or allocate a new centroid, and compress/reinsert when full.
- Per-stat errors increment a capped `errs` field via `VS_INCERRS()`.

## Rendering and Visiting
- `stats_v1_blob_iter()` iterates VOIs and voistats with flags for first/last callback, VOI, and voistat.
- `stats_v1_blob_tostr()` renders freeform or JSON output, optionally including template metadata and object-dump internals.
- `stats_voistatdata_tostr()` renders primitive numeric, Q, histogram, t-digest, and VOISTATE data.
- `stats_v1_blob_visit()` exposes each stat through a caller-provided callback with `struct sb_visit`.

## Kernel Integration
- Uses `rwlock` in kernel and `pthread_rwlock_t` in userland compatibility builds for global template list protection.
- Kernel allocation uses `M_STATS`; userland mode uses libc allocation wrappers.
- Exposes `kern.stats.templates` sysctl for available templates.
- `stats_tpl_sample_rates()` is a reusable sysctl handler for subsystem-specific template sampling rate lists. It renders and parses CSV-like `template:hash=percent` specifications, validates cumulative sampling at <=100%, and calls subsystem callbacks to get/put rate arrays.
- `stats_tpl_sample_rollthedice()` chooses a sampled template using either PRNG output or deterministic hash of seed bytes.

## Concurrency and Invariants
- Global template list is protected by `TPL_LIST_*` locks.
- Template mutation is under write lock; blob instance updates appear caller-synchronized and are not internally locked.
- Blob offsets are 16-bit; `SB_V1_MAXSZ` prevents v1 blobs from exceeding 65535 bytes.
- Numerous `KASSERT`s guard ABI layout, stat initialization, type validity, t-digest tree consistency, and size/offset expectations.

## Notable Limitations and Risks
- Existing VOI expansion is not implemented.
- `stats_v1_blob_finalise()` is a stub.
- Histogram update uses a linear reverse bucket scan.
- T-digest compression uses pseudo-random centroid reinsertions and contains comments about fidelity/underflow tracking not yet implemented.
- Template uniqueness after hash update is noted but not fully enforced after VOI additions.
