# SentinelLab ASIR · Sistemas, redes y detección SSH

**Autor:** Alejandro Oliach Andreu  
**Tipo:** proyecto educativo de ASIR orientado a sistemas, redes y Blue Team.

Proyecto para practicar segmentación de redes, administración Linux y análisis
defensivo de registros. Incluye una red simulada en Cisco Packet Tracer y un
laboratorio con máquinas virtuales Debian, además de un analizador SSH en Python.

## Estado actual

| Componente | Estado |
|---|---|
| Analizador SSH y generación de informes JSON | Implementado |
| Dashboard HTML, CSS y JavaScript | Implementado |
| Red con VLAN y ACL en Packet Tracer | Validada en simulación |
| Cliente y servidor Debian en VirtualBox | Configurados y comunicados por SSH |
| Análisis de registros reales del laboratorio | Validado con cinco fallos y un acceso correcto |
| Hardening Linux, firewall y backups | Pendientes de implementación y validación |
| Integración con Wazuh | Ampliación futura |

La red de Packet Tracer y las VM de VirtualBox son prácticas independientes.
Las VLAN y ACL simuladas no protegen la red de las VM.

El análisis de registros es manual: se exporta el log del servidor, se transfiere
a Windows y se procesa con Python. No existe monitorización en tiempo real.

## Casos prácticos y evidencias

- [Segmentación con VLAN y ACL en Cisco Packet Tracer](docs/packet-tracer/README.md).
- [Laboratorio SSH con Debian y VirtualBox](docs/linux-lab/evidence/README.md).
- [Registro real exportado del laboratorio](docs/linux-lab/evidence/ssh-auth.log).
- [Informe generado con ese registro](docs/linux-lab/evidence/report.json).

## Ejecutar el proyecto

Requiere Python 3.10 o posterior, sin dependencias externas.
Ejecuta los comandos desde la raíz del repositorio.
En Linux puede ser necesario utilizar `python3` en lugar de `python`.

### Muestra sintética y dashboard

```bash
python scripts/analyze_auth.py --input data/sample_auth.log --output docs/dashboard/report.json
python -m unittest discover -s tests -v
python -m http.server 8000 --directory docs/dashboard
```

Abre <http://localhost:8000/>.

La muestra sintética contiene 11 líneas: 10 eventos SSH y una línea de cron.
Con los parámetros predeterminados se obtienen 8 fallos, 2 accesos correctos
y 2 alertas.

El dashboard muestra el contenido de `docs/dashboard/report.json`.
No recoge registros del servidor automáticamente.

### Registro real del laboratorio

```bash
python scripts/analyze_auth.py --input docs/linux-lab/evidence/ssh-auth.log --output report-local.json
```

Resultado observado con los parámetros predeterminados:

| Métrica | Resultado |
|---|---:|
| Líneas leídas | 13 |
| Eventos de autenticación | 6 |
| Fallos | 5 |
| Accesos correctos | 1 |
| Alertas | 2 |

El informe contiene una alerta `repeated_ssh_failures` y otra
`ssh_success_after_failures`, ambas para la IP del cliente `192.168.50.20`.

Este comando genera un informe separado; no cambia el informe del dashboard.

## Formatos de registro admitidos

El parser reconoce:

- `Failed password` y `Accepted password`.
- `Failed publickey` y `Accepted publickey`.
- Identificadores `sshd[PID]:` y `sshd-session[PID]:`.
- Marcas temporales ISO 8601 con zona horaria.
- Direcciones IPv4 e IPv6 válidas, normalizadas mediante `ipaddress`.

Cada evento interno conserva el usuario, la IP, la fecha, el resultado
y el método de autenticación (`auth_method`).

Se admite un sufijo opcional con detalles de la clave pública.
Su contenido no se verifica criptográficamente.

El formato de texto exportado mediante `journalctl -o short-iso` se ha
validado con autenticación por contraseña en el laboratorio Debian.
El soporte de clave pública se ha comprobado mediante pruebas unitarias.

### Contadores de parsing

| Campo | Significado |
|---|---|
| `total_lines` | Líneas leídas |
| `parsed_events` | Eventos de autenticación interpretados |
| `non_ssh_lines` | Líneas sin un identificador SSH reconocido |
| `unparsed_ssh_lines` | Líneas con identificador SSH reconocido que no producen un evento |

`non_ssh_lines` es una clasificación por identificador de proceso:
puede incluir mensajes auxiliares de autenticación como los de `unix_chkpwd`.

Los mensajes PAM de `sshd-session` se contabilizan como SSH no interpretado.
No se cuentan como intentos adicionales de contraseña.

Una línea no interpretada puede contener un mensaje no soportado
o datos inválidos; no implica por sí sola actividad maliciosa.

## Reglas de detección

Los eventos se ordenan por fecha antes de aplicar las reglas.

| Regla | Agrupación | Umbral predeterminado |
|---|---|---|
| `repeated_ssh_failures` | IP de origen | 5 fallos |
| `ssh_success_after_failures` | IP de origen y usuario | 3 fallos anteriores al éxito |

Ambas reglas utilizan una ventana de 15 minutos por defecto.

### Fallos repetidos

Se genera una alerta cuando una IP alcanza el umbral dentro de la ventana.
Los siguientes fallos del mismo episodio no generan alertas duplicadas.

La detección se rearma cuando no quedan fallos anteriores de esa IP
dentro de la ventana. Con el valor predeterminado, una pausa de más
de 15 minutos permite iniciar otro episodio; el límite exacto de
15 minutos está incluido.

Una secuencia continua puede mantener un único episodio durante mucho tiempo.
No se generan recordatorios periódicos.

### Acceso correcto tras fallos

Solo se correlacionan los fallos de la misma IP y el mismo usuario.
Cada acceso correcto reinicia ese historial, genere o no una alerta.
El historial general de fallos por IP se conserva.

Esta alerta es un indicio que investigar, no una confirmación de compromiso.
En el laboratorio se generó mediante intentos controlados.

### Parámetros

| Opción | Función | Valor predeterminado |
|---|---|---:|
| `--threshold` | Umbral de fallos repetidos | 5 |
| `--success-threshold` | Fallos previos necesarios para alertar tras un éxito | 3 |
| `--window-minutes` | Ventana temporal de ambas reglas, en minutos | 15 |

Los tres valores deben ser mayores que cero.

## Pruebas y validación

La suite contiene 25 métodos de prueba y se ha ejecutado correctamente
en local. Cubre:

- Parsing de autenticación por contraseña y clave pública.
- Identificadores `sshd` y `sshd-session`.
- IP inválida, normalización IPv6, fecha inválida y ausencia de zona horaria.
- Contadores de parsing y clasificación de mensajes PAM.
- Umbrales, ráfagas separadas, ausencia de duplicados y límites temporales.
- Correlación por usuario y reinicio del historial tras un acceso correcto.

Además de las pruebas sintéticas, se ha procesado el registro real
incluido en el laboratorio Debian: 13 líneas, 6 eventos y 2 alertas.

Esta validación cubre el escenario documentado; no demuestra compatibilidad
con todas las versiones de OpenSSH ni con todos los formatos de registro.

## Limitaciones

- No interpreta syslog tradicional sin año y zona horaria ni la salida JSON
  de `journalctl`.
- Otros identificadores de proceso pueden clasificarse como `non_ssh_lines`.
- Carga los eventos en memoria y procesa archivos completos.
- El estado solo existe durante la ejecución; reanalizar un archivo vuelve
  a generar sus alertas.
- La correlación no distingue servidores de destino. La validación actual
  utiliza registros de un único servidor.
- `auth_method` se conserva en los eventos internos, pero no se muestra
  en las alertas ni en el dashboard.
- No bloquea direcciones IP ni ejecuta respuestas automáticas.

## Conocimientos practicados

- **Linux:** usuarios, sudo, servicios systemd, OpenSSH y consulta del journal.
- **Redes:** direccionamiento IPv4, conectividad, VLAN, trunk 802.1Q,
  routing inter-VLAN y ACL extendidas.
- **Python:** expresiones regulares, validación de datos, correlación temporal,
  CLI, JSON y pruebas unitarias.
- **Blue Team:** interpretación de registros, reglas de detección,
  identificación de limitaciones y conservación de evidencias.
- **Git y GitHub:** ramas, revisión de cambios y documentación técnica.

## Próximos pasos

1. Configurar y validar autenticación SSH mediante clave pública en las VM.
2. Aplicar hardening básico y reglas de firewall con pruebas documentadas.
3. Ampliar los escenarios de detección antes de valorar un SIEM.

La [guía de hardening](docs/hardening-linux.md) es material de trabajo;
su presencia no acredita que sus medidas estén aplicadas.

## Uso y publicación de evidencias

Proyecto educativo para sistemas propios o autorizados.
Los registros reales incluidos proceden del laboratorio y utilizan
direccionamiento privado; la muestra sintética emplea IP de documentación.

No publicar contraseñas, claves privadas, tokens ni registros de terceros.
Las reglas son didácticas y no sustituyen una plataforma de monitorización
ni un proceso de respuesta a incidentes.