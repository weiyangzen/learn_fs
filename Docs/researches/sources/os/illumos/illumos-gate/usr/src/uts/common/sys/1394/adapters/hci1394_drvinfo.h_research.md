# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/1394/adapters/hci1394_drvinfo.h

This header centralizes driver-wide information shared by the `hci1394` HAL modules.

Main types:
- `hci1394_statevar_t`: HAL lifecycle state, with `INITIAL`, `BUS_RESET`, `NORMAL`, and `SHUTDOWN`.
- `hci1394_drvstate_t`: protected state plus mutex.
- `hci1394_stats_t`: bus reset, self-ID, and PHY interrupt/error counters.
- `hci1394_drvinfo_t`: shared driver metadata including `dev_info_t`, services-layer private pointer, instance, generation count, state, stats, interrupt block cookie, and register/buffer access attributes.

Dependencies include DDI/SunDDI and `h1394.h`, tying this private driver metadata to the 1394 services/HAL contract. Warlock annotations mark the struct as single-thread modified, with mutex fields embedded for runtime coordination.
