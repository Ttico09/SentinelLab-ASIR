# Laboratorio SSH con Debian y VirtualBox

## Objetivo

Validar el analizador de SentinelLab con registros reales generados
mediante intentos de autenticación controlados en un laboratorio propio.

## Entorno

- Servidor Debian 13: 192.168.50.10/24, servicio OpenSSH.
- Cliente Debian 13: 192.168.50.20/24.
- Ambas máquinas conectadas a la red interna de VirtualBox `sentinellab`.
- Sin puerta de enlace ni DNS para las pruebas entre ambas máquinas.
- Análisis del archivo exportado realizado en Windows con Python.

## Procedimiento

1. Comprobar la conectividad IP entre cliente y servidor.
2. Verificar el acceso SSH.
3. Registrar el instante de inicio en la consola del servidor:

   `inicio=$(date --iso-8601=seconds)`

4. Desde el cliente, iniciar SSH permitiendo seis solicitudes de contraseña:

   `ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no -o NumberOfPasswordPrompts=6 user@192.168.50.10`

5. Introducir cinco contraseñas incorrectas y después la correcta.
6. Exportar los registros desde la misma terminal del servidor:

   `sudo journalctl -u ssh.service --since "$inicio" -o short-iso --no-pager > ~/sentinellab-ssh-prueba.log`

7. Transferir el archivo al cliente mediante SCP y a Windows mediante
   una carpeta compartida de VirtualBox.

## Limitación detectada y corrección

Los eventos de autenticación observados utilizan `sshd-session[PID]`.
El parser anterior solo reconocía `sshd[PID]`.

Se añadió una prueba unitaria que reprodujo el fallo y se ampliaron
las expresiones regulares para admitir ambos nombres. También se
comprobó que los mensajes PAM de `sshd-session` se clasifican como
SSH no interpretado, sin generar eventos de autenticación duplicados.

## Resultados observados

| Métrica | Resultado |
|---|---:|
| Líneas totales | 13 |
| Eventos interpretados | 6 |
| Líneas clasificadas como no SSH | 5 |
| Líneas SSH no interpretadas | 2 |
| Autenticaciones fallidas | 5 |
| Autenticaciones aceptadas | 1 |
| Alertas | 2 |

Alertas generadas con los parámetros predeterminados:

- `repeated_ssh_failures`: cinco fallos desde 192.168.50.20.
- `ssh_success_after_failures`: acceso de `user` desde esa misma IP
  tras cinco fallos.

Son actividades controladas del laboratorio. Una alerta de acceso
tras fallos no demuestra por sí sola que exista un compromiso.

## Evidencias y reproducción

- [Registro original exportado](evidence/ssh-auth.log)
- [Informe generado](evidence/report.json)

Desde la raíz del repositorio:

    python scripts/analyze_auth.py --input docs/linux-lab/evidence/ssh-auth.log --output report-local.json

Esta validación cubre autenticación por contraseña y el formato
exportado mediante `journalctl -o short-iso`. No demuestra todavía
el funcionamiento con todos los formatos o escenarios SSH.