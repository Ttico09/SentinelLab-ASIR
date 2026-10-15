# Diseño de arquitectura (objetivo técnico)

## Alcance

Red interna totalmente aislada para aprender segmentación, administración, registros, supervisión y detección de anomalías. Ningún elemento requiere exponer servicios a Internet.

## Subredes propuestas

| Zona | VLAN | Red | Gateway | Uso |
|---|---:|---|---|---|
| Gestión | 10 | 192.168.10.0/24 | 192.168.10.1 | Estación de administración |
| Usuarios | 20 | 192.168.20.0/24 | 192.168.20.1 | Clientes de prueba |
| Servidores | 30 | 192.168.30.0/24 | 192.168.30.1 | Linux y monitorización |

**Regla principal:** denegar tráfico inter-VLAN no autorizado; permitir exclusivamente flujos que tengan una necesidad documentada. El diseño debe verificar esta política con pruebas positivas y negativas.

## Recursos

- Primera fase: un PC con Python 3.10+, sin máquinas virtuales.
- Segundo paso: Cisco Packet Tracer para montar una topología simulada.
- Más adelante: VirtualBox/VMware/Proxmox, una VM Debian y un cliente de pruebas.
- SIEM Wazuh: fase opcional, ajustar recursos según requisitos oficiales del despliegue seleccionado.

## Seguridad y validación

- Documentar política de acceso entre VLAN y el motivo de cada excepción.
- Mantener el host y las VM al día; activar logs y limitar SSH a la zona de gestión.
- Separar cuentas administrativas de usuarios comunes.
- Recoger pruebas: `ping` permitido/denegado, servicios esperados, logs y resultados del panel.
- **No subir claves privadas, exportaciones de VM, contraseñas o logs reales al repositorio público.**
