# File Research: sources/os/bsd/freebsd-src/sbin/ipfw/dummynet.c

## Purpose

`dummynet.c` implements userland support for FreeBSD dummynet objects in the `ipfw`/`dnctl` CLI. It parses `pipe`, `queue`/`flowset`, and `sched` configuration commands; formats kernel-returned dummynet object lists; deletes and flushes dummynet objects; loads empirical delay profile files; and supports RED/GRED plus newer AQM scheduler parameters for CoDel, FQ-CoDel, PIE, and FQ-PIE.

The file speaks the dummynet kernel ABI through `IP_DUMMYNET3` using packed `dn_id`-based TLV-like buffers from `<netinet/ip_dummynet.h>`.

## Public Surface

Exported functions declared in `ipfw2.h`:

- `void ipfw_config_pipe(int ac, char **av)`: parses and submits `pipe N config`, `queue N config`, and `sched N config`.
- `void dummynet_list(int ac, char *av[], int show_counters)`: handles dummynet `list`/`show`.
- `void dummynet_flush(void)`: sends a dummynet flush command.
- `int ipfw_delete_pipe(int pipe_or_queue, int n)`: deletes a pipe, queue/flowset, or scheduler.

Internal helpers include:

- `oid_fill()` and `o_next()` for building request objects in a contiguous buffer.
- `read_bandwidth()` for parsing numeric bandwidths and suffixes.
- `load_extra_delays()` for profile file parsing and interpolation.
- `process_extra_parms()` for CoDel/PIE/FQ parameter parsing.
- `list_pipes()` and related print helpers for rendering kernel responses.
- `parse_range()` for dummynet list filters.

## Main Data and Tokens

`dummynet_params[]` maps CLI words to shared parser tokens from `ipfw2.h`, covering packet loss, masks, queue sizes, RED/GRED, AQM names, bandwidth, delay, scheduler type, IPv4/IPv6 mask fields, profiles, and burst.

With `NEW_AQM` defined locally, `aqm_params[]` maps AQM option names such as `target`, `interval`, `flows`, `quantum`, `tupdate`, `alpha`, `beta`, `ecn`, `capdrop`, `dre`, and `derand`.

The code builds and interprets kernel structures including `dn_sch`, `dn_link`, `dn_fs`, `dn_profile`, `dn_flow`, and `dn_extra_parms`. `g_co.do_pipe` selects the dummynet object class:

- `1`: pipe/link compatibility path.
- `2`: queue/flowset.
- `3`: scheduler.

## Configuration Flow

`ipfw_config_pipe()` is the central parser. It allocates one contiguous command buffer large enough for the command header, scheduler, link, flowset, optional profile, and optional AQM/scheduler extra-parameter blocks. It then:

1. Skips `config` and parses the numeric object id.
2. Builds a different initial object layout depending on `g_co.do_pipe`.
3. Initializes fields to sentinel values when the kernel should reuse existing state.
4. Walks remaining arguments and mutates `dn_sch`, `dn_link`, `dn_fs`, masks, profile, or extra parameter objects.
5. Validates queue limits, delay bounds, RED thresholds, ECN compatibility, and sysctl-derived dummynet limits.
6. Sends the packed command with `do_cmd(IP_DUMMYNET3, ...)`.

Pipe configuration creates a scheduler, link, and FIFO flowset for backward compatibility. Queue configuration only emits a flowset. Scheduler configuration emits a scheduler and a default flowset for non-multiqueue schedulers.

## AQM Handling

The file compiles with `NEW_AQM` enabled. AQM handling is split between:

- `process_extra_parms()`: consumes the remaining argument vector after `codel`, `fq_codel`, `pie`, `fq_pie`, or scheduler `type fq_*`, stores parsed values in `dn_extra_parms.par[]`, and uses `-1` to request kernel defaults.
- `get_extra_parms()`: issues `DN_CMD_GET` requests for `DN_AQM_PARAMS` or `DN_SCH_PARAMS` and formats kernel-returned parameter arrays for listing.

Time values are converted through `time_to_us()` and `us_to_time()`. PIE floating parameters are scaled with `PIE_SCALE` and `PIE_FIX_POINT_BITS`.

One important behavior: selecting `fq_codel`/`fq_pie` through the scheduler `type` consumes the remaining arguments as scheduler-specific parameters, so ordering on the command line is significant.

## Listing and Formatting

`dummynet_list()` builds a `DN_CMD_GET` request, optionally embeds ranges parsed by `parse_range()`, estimates or retries response buffer size, then passes the response to `list_pipes()`.

`list_pipes()` expects the kernel response order described in comments:

- Pipes/schedulers: link, scheduler, internal flowset, instances.
- Flowsets: flowset then queues.

It switches by `oid->type` and renders links, schedulers, flowsets, profiles, flows, child-flowset lists, and unknown objects. Flow formatting supports both IPv4 and IPv6 `ipfw_flow_id` layouts.

`print_flowset_parms()` prints queue size, packet-loss rate, RED/GRED/AQM mode, buckets, scheduler id, weight, `lmax`, priority, and masks. `print_mask()` handles IPv4 and IPv6 masks.

## Delay Profiles

`load_extra_delays()` parses an external profile file with tokens:

- `samples`
- `loss-level`
- `name`
- `bw`
- `delay prob` or `prob delay`

It validates counts and probabilities, sorts points by probability/delay, interpolates delays into `dn_profile.samples[]`, and stores loss and profile name. It requires at least two data points and defaults missing sample count to 100 and missing loss level to no loss.

## Kernel and System Dependencies

This file depends on:

- `do_cmd()` from `ipfw2.c` for `IP_DUMMYNET3` socket operations.
- `g_co` for global command flags, especially `do_pipe`, `verbose`, and sort/list flags.
- `n2mask()` from `ipfw2.c` for IPv6 masks.
- `sysctlbyname()` for queue-size and RED defaults/limits.
- `expand_number()` and `humanize_number()` from libutil for burst/list display.

## Error Handling and Risks

The parser mostly fails fast with `errx()`/`err()` on malformed commands. Buffer construction uses explicit object lengths and `safe_calloc()`/`safe_realloc()`, but correctness depends on keeping packed object lengths aligned with kernel ABI structures.

Risk points:

- `process_extra_parms()` consumes all remaining arguments after an AQM token; invalid tokens only print a diagnostic and continue, rather than failing in every default case.
- `ipfw_delete_pipe()` overwrites the requested id variable with the `do_cmd()` return and then warns using `rule %u` with `i` reset to `1`, so warnings do not preserve the original object id.
- Delay-profile parsing stores up to `ED_MAX_SAMPLES_NO` points but increments `points_no` without an immediately adjacent explicit bounds check in the data-point branch; the sample count is checked separately.
- Several formatting buffers are fixed-size stack buffers; expected strings are bounded by kernel ABI names and address lengths, but new AQM names/parameters should be checked carefully if extended.

## Testing Notes

Useful coverage would include:

- `dnctl pipe N config` with bandwidth units, byte/slot queue sizes, burst, masks, and delay bounds.
- RED/GRED validation including ECN threshold rules.
- CoDel, PIE, FQ-CoDel, and FQ-PIE parameter parsing with default, numeric, time-unit, and invalid tokens.
- Delay profile files with missing defaults, sorted/unsorted points, duplicate headers, invalid probability, and too few samples.
- Listing responses with IPv4 flows, IPv6 flows, schedulers, profiles, and range filters.
