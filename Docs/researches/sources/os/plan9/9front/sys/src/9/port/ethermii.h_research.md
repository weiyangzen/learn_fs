# File Research: sources/os/plan9/9front/sys/src/9/port/ethermii.h

Defines MII register numbers, status/control bit masks, autonegotiation advertisements, 1000BASE-T master/slave bits, extended status bits, and MMD multi-gigabit control/status bits.

It defines `Mii`, containing PHY array, current PHY, controller name/context, and read/write hooks, plus `MiiPhy`, containing identity, advertised capabilities, link result fields, and optional page-register mapper. It declares all generic MII helper functions and `addmiibus`/`delmiibus` hooks.
