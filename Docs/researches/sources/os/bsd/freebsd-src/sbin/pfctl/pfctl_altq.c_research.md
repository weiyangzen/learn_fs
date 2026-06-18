# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/pfctl_altq.c

## Purpose

`pfctl_altq.c` implements pfctl’s ALTQ queueing support. It stores parsed ALTQ and queue definitions, resolves queues by interface/name, computes scheduler-specific parameters, validates queue hierarchies before commit, and prints ALTQ configuration.

Supported schedulers in this file include:
- CBQ
- PRIQ
- HFSC
- FAIRQ
- CODEL

## Initialization And Maps

The file keeps:
- `interfaces`: STAILQ of interface-level ALTQ definitions.
- `queue_map`: hash table keyed by `ifname:qname`.
- `if_map`: hash table keyed by interface name.
- `qid_map`: hash table keyed by queue name.

`pfctl_altq_init()` is a constructor that creates all three hash tables with `hcreate_r()`.

`pfaltq_store()` copies a `struct pf_altq` into pfctl-owned storage:
- Interface entries are inserted into `if_map` and `interfaces`.
- Queue entries are inserted into `queue_map`.
- Queue names are mapped to queue IDs through `qid_map`.

Lookup helpers:
- `pfaltq_lookup(ifname)`
- `qname_to_pfaltq(qname, ifname)`
- `qname_to_qid(qname)`

The queue ID lookup enforces the convention that queues with the same name across interfaces share the same ID.

## Printing

`print_altq()` prints top-level `altq on <if>` definitions, scheduler options, bandwidth, qlimit, and token bucket size.

`print_queue()` prints queue definitions, optionally including the interface, bandwidth, priority, qlimit, and scheduler options.

Scheduler option printers:
- `print_cbq_opts()`
- `print_priq_opts()`
- `print_hfsc_opts()`
- `print_fairq_opts()`
- `print_codel_opts()`

Service curve printers:
- `print_hfsc_sc()`
- `print_fairq_sc()`

`rate2str()` formats bit rates into compact `b`, `Kb`, `Mb`, or `Gb` strings using a static ring of buffers.

## Evaluating Top-Level ALTQ

`eval_pfaltq()` computes interface-level ALTQ parameters:
- Uses absolute bandwidth if supplied.
- Otherwise queries interface speed through `getifspeed()`.
- Applies percent bandwidth specifications.
- Caps bandwidth to `UINT_MAX` for non-HFSC schedulers.
- Evaluates queue options.
- Computes default `tbrsize` from interface bandwidth and MTU when omitted.

`getifspeed()` queries `SIOCGIFDATA`.

`getifmtu()` queries `SIOCGIFMTU`; on FreeBSD failure it falls back to 1500.

## Evaluating Queues

`eval_pfqueue()` resolves a parsed queue against its parent interface and optional parent queue. It:
- Copies scheduler and interface bandwidth from the top-level ALTQ definition.
- Rejects duplicate queue names on the same interface.
- Resolves or assigns queue IDs.
- Resolves parent queues and parent queue IDs.
- Sets default qlimit.
- Computes queue bandwidth for CBQ/HFSC/FAIRQ.
- Checks child bandwidth against interface and parent bandwidth for non-HFSC schedulers.
- Applies scheduler-specific options with `eval_queue_opts()`.
- Tracks parent child counts.
- Dispatches to scheduler-specific evaluation functions.

`eval_queue_opts()` copies parsed option structures into the kernel `pf_altq` union and resolves bandwidth specifications in HFSC/FAIRQ service curves.

`eval_bwspec()` converts an absolute or percent bandwidth specification into a numeric bandwidth, capped to the reference bandwidth.

## Commit Validation

`check_commit_altq()` walks every interface-level ALTQ entry and runs scheduler-specific validation:
- `check_commit_cbq()`: requires exactly one root queue and exactly one default queue.
- `check_commit_priq()`: requires exactly one default queue.
- `check_commit_hfsc()`: requires exactly one default queue.
- `check_commit_fairq()`: requires exactly one default queue.

The result is used by `pfctl_rules()` before committing an ALTQ transaction.

## CBQ Support

`eval_pfqueue_cbq()` validates priority, sets packet-size defaults from MTU, marks root queues, counts root/default classes, and computes CBQ timing parameters.

`cbq_compute_idletime()` computes:
- `ns_per_byte`
- `maxidle`
- `minidle`
- `offtime`
- `minburst`
- `maxburst`

It uses CBQ’s filter gain constants and clamps values that would overflow kernel integer fields for very low bandwidth queues.

CBQ option flags printed include RED, ECN, RIO, CODEL, clear DSCP, flowvalve, borrow, WRR, efficient, root, and default.

## PRIQ Support

`eval_pfqueue_priq()` validates priority range, enforces unique queue priority per interface via a bitset, and counts default classes.

PRIQ option flags printed include RED, ECN, RIO, CODEL, clear DSCP, and default.

## HFSC Support

`eval_pfqueue_hfsc()` handles HFSC hierarchy and service-curve admission:
- Root queue gets interface-bandwidth linkshare.
- First child initializes parent real-time and linkshare generalized service curves.
- A default queue cannot have children.
- Missing linkshare `m2` defaults to queue bandwidth.
- Convex curve constraints are validated.
- Real-time curves are limited to 80% of interface bandwidth.
- Child linkshare sum must fit under the parent curve.
- Upper-limit curves must not exceed interface bandwidth and must not be lower than real-time curves.

HFSC options printed include RED, ECN, RIO, CODEL, clear DSCP, default, realtime, linkshare, and upperlimit.

## FAIRQ Support

`eval_pfqueue_fairq()` is similar to HFSC but only validates link-sharing curves:
- Root queue gets interface-bandwidth linkshare.
- Default queue cannot have children.
- Missing linkshare `m2` defaults to queue bandwidth.
- Child linkshare sum must fit under the parent FAIRQ curve.

FAIRQ options printed include RED, ECN, RIO, CODEL, clear DSCP, default, and linkshare.

## Generalized Service Curve Math

The file implements an internal generalized service curve representation using `struct segment`.

Functions:
- `gsc_add_sc()`: adds a two-piece service curve into a generalized curve.
- `is_gsc_under_sc()`: checks if a generalized curve is no greater than a target service curve.
- `gsc_getentry()`: finds or creates a segment boundary at a given x-coordinate.
- `gsc_add_seg()`: adds a segment contribution across a curve interval.
- `sc_x2y()`: projects a service curve to y at x.

This code is central to HFSC/FAIRQ admission control.

## Role In This Group

`pfctl_altq.c` is the queueing and traffic-shaping companion to the main pfctl loader. It translates human-readable ALTQ queue syntax into scheduler-specific kernel structures while enforcing hierarchy and bandwidth invariants before rules are committed.
