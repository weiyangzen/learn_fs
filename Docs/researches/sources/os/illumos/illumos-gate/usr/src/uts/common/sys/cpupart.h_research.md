# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/cpupart.h

## Role

Defines CPU partition structures and APIs used by processor sets, dispatching, load averages, lgroups, and CMT processor groups.

## Key Types

- `cpupartid_t`: integer partition id.
- `CP_DEFAULT`: default partition id.
- `CP_ALL`, `CP_NONEMPTY`: `cpupart_list()` filters.
- `cpupart_t`: partition state:
  - partition-wide kernel preemption queue.
  - id, CPU count, partition list links.
  - CPU list and kstat.
  - runnable/running counts.
  - cumulative load statistics.
  - load average data.
  - lgroup set/load table, generation, hint.
  - attributes.
  - CMT PG bitset.
  - halted CPU bitset.
- `cpupart_kstat_t`: named kstat fields for updates, runnable/waiting totals, CPU count, and load averages.

## Scheduling Macros

- `CP_MAXRUNPRI(cp)`: maximum run priority for a partition global queue.
- `DISP_MUST_SURRENDER(t)`: checks whether a thread must yield to higher-priority runnable work on local or partition queues.

## Globals

- `cp_default`
- `cp_list_head`
- `cp_numparts`
- `cp_numparts_nonempty`
- `cp_haltset_fanout`

## APIs

Includes initialization, lookup, create/destroy, CPU attach/query/list, thread binding, kernel preempt queue allocation, load averages, partition listing, and attribute get/set.

## Research Relevance

Important for scheduling topology, processor sets, CPU partition load accounting, and how zones/projects can be isolated at CPU level.
