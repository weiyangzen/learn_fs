# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mii.h

Purpose: Declares the generic MII/PHY support framework for MAC drivers.

Key model:
- Drivers provide `mii_ops_t` callbacks for PHY register read/write, link notification, and optional reset.
- MII framework calls driver entry points asynchronously from a taskq and holds internal locks, so drivers must not hold their own locks across calls into MII.

Key APIs:
- Lifecycle: `mii_alloc()`, `mii_alloc_instance()`, `mii_free()`.
- Control: `mii_set_pauseable()`, `mii_reset()`, `mii_start()`, `mii_stop()`, `mii_resume()`, `mii_suspend()`, `mii_probe()`, `mii_check()`.
- Query: PHY address/id, speed, duplex, state, flow control.
- Loopback support: `mii_get_loopmodes()`, `mii_set_loopback()`, `mii_get_loopback()`, `mii_m_loop_ioctl()`.
- MAC callback helpers: `mii_m_getprop()`, `mii_m_setprop()`, `mii_m_propinfo()`, `mii_m_getstat()`.

Important details:
- Monitoring starts only after `mii_start()`.
- `mii_stop()` and `mii_suspend()` guarantee the MII layer is no longer executing driver entry points on return.
- Helper functions are designed to reduce repetitive MAC driver property/stat/ioctl code.

Relevance to subset A: Network driver support, outside filesystem focus.
