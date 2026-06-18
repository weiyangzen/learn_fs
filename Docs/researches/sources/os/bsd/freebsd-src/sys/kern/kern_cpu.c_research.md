# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_cpu.c

## Purpose
Provides the MI cpufreq framework that exposes CPU frequency control through per-CPU `cpufreq` child devices and sysctls, combines hardware driver settings into usable frequency levels, and coordinates frequency changes across CPUs.

## Main Elements
- Driver framework:
  - Defines `cpufreq` bus methods for probe, attach, detach, set, get, and levels.
  - `cpufreq_register()` adds per-driver `freq_settings` sysctl, creates one `cpufreq` child per CPU, and records the backing hardware frequency driver.
  - `cpufreq_unregister()` removes the cpufreq child.
- State and sysctls:
  - `struct cpufreq_softc` tracks current level, priority, saved frequencies, synthesized levels, nominal max MHz, driver device, sysctl context, startup task, and reusable level buffer.
  - `dev.cpu.N.freq` reads or sets current CPU frequency.
  - `dev.cpu.N.freq_levels` reports synthesized `freq/power` levels.
  - `debug.cpufreq.lowest` filters low frequencies; `debug.cpufreq.verbose` enables debug prints.
- Frequency changes:
  - `cf_set_method()` invokes pre/post event handlers, enforces priority, restores saved levels when requested, rejects levels below threshold, binds the current thread to target CPUs, raises priority, calls driver set methods, and caches the active level.
  - Higher-priority changes save the previous level for later restoration.
- Frequency discovery:
  - `cf_get_method()` returns cached frequency unless the driver is uncached, otherwise queries the driver, matches supported levels, or estimates clockrate.
  - `cf_levels_method()` collects absolute and relative driver settings, supplies a synthetic 100% absolute level if needed, expands relative percentages, filters by threshold, and returns sorted levels.
- Level synthesis:
  - `cpufreq_insert_abs()` inserts absolute settings in frequency order.
  - `cpufreq_expand_set()` combines relative settings with absolute levels.
  - `cpufreq_dup_set()` creates derived levels, rejects duplicate or less efficient derived combinations, and updates total frequency, power, and latency.
- Notifications:
  - Startup task calls `cpufreq_settings_changed()`, which invokes `cpufreq_levels_changed`.

## Dependencies And Integration
Uses `cpufreq_if` driver methods, device/bus APIs, per-CPU lookup, scheduler binding, eventhandlers, sysctl, taskqueue, SMP startup state, and clockrate estimation.

## Risk Notes
Frequency changes are scheduler- and SMP-sensitive. The code avoids changing only the boot CPU before AP startup, binds to target CPUs during driver calls, and restores thread priority/binding afterward. The level-composition algorithm can grow combinatorially, capped by `CF_MAX_LEVELS`, and partial driver-set failures are noted without full rollback.
