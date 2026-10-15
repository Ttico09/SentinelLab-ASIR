# Práctica de Cisco Packet Tracer — segmentación

**Estado: PENDIENTE.** Aquí guardarás un fichero `.pkt` creado por ti y las capturas de la topología.

## Propuesta de práctica

1. Crea 1 router, 1 switch administrable, 3 PCs y 1 servidor en Packet Tracer.
2. Configura VLAN 10 (Gestión), VLAN 20 (Usuarios) y VLAN 30 (Servidores).
3. Configura puertos access y un troncal 802.1Q entre switch y router.
4. En el router, crea subinterfaces dot1Q y gateways `192.168.10.1`, `192.168.20.1` y `192.168.30.1`.
5. Asigna a cada máquina una IP de su subred con máscara `/24` y la puerta de enlace adecuada.
6. Comprueba conectividad inter-VLAN antes de aplicar controles.
7. Introduce una ACL que deniegue conexiones iniciadas desde la red de usuarios hacia el servidor de gestión; mantén los servicios estrictamente necesarios.
8. Registra capturas y resultados con los comandos `show vlan brief`, `show interfaces trunk`, `show ip interface brief`, `show access-lists` y pruebas de conexión.
9. Anota una incidencia deliberada (p. ej., una puerta de enlace incorrecta), sus síntomas y la corrección.

## Evidencias esperadas

- Archivo `sentinellab-topologia.pkt`.
- Capturas de VLANs, routing y ACLs aplicadas.
- Tabla de pruebas: origen, destino, protocolo, esperado, resultado real.

**Nota:** no copies configuraciones indiscriminadamente. Justifica cada regla de la ACL y valida ambos sentidos del tráfico.
