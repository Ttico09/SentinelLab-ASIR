# SentinelLab ASIR · Portfolio de ciberseguridad

> Plantilla para importar o pegar en Notion. Actualiza el estado a medida que completes el trabajo.

## Resumen ejecutivo

Laboratorio personal para demostrar competencias de administración de sistemas, redes, programación y seguridad defensiva adquiridas durante ASIR.

## Mi papel

Diseño, implementación, validación y documentación individual del laboratorio.

## Objetivo profesional

Prácticas de ASIR en ciberseguridad, análisis SOC L1, sistemas o redes.

## Tecnologías

- **Implementado en versión inicial:** Python, JSON, HTML, CSS y JavaScript.
- **Planificado:** Cisco Packet Tracer, VLAN, ACL, Debian/Ubuntu, SSH y firewall; SIEM Wazuh opcional.

## Fases y evidencias

| Fase | Qué demostrar | Evidencia (enlace/captura) | Estado |
|---|---|---|---|
| Analizador de eventos | Código, tests, JSON y alertas | [Añadir enlace] | Versión inicial |
| Segmentación | Topología, VLAN, ACL, pruebas | [Añadir enlace] | Pendiente |
| Administración Linux | Gestión de usuarios, SSH, firewall, backup | [Añadir enlace] | Pendiente |
| Monitorización SIEM | Reglas y análisis de alertas | [Añadir enlace] | Pendiente |

## Caso de uso: detección de fallos SSH

**Contexto:** registros sintéticos de un servidor de laboratorio.  
**Hipótesis:** varios fallos de autenticación desde una misma IP durante una ventana breve deben generar una alerta.  
**Método:** analizador Python con ventana temporal y umbral configurable.  
**Validación:** `python -m unittest discover -s tests -v`; revisar `report.json`.  
**Limitaciones:** los logs están simplificados; se necesita adaptar el parser antes de procesar registros reales.  
**Aprendizaje:** [Escribir qué problema tuviste, cómo lo resolviste y qué mejorarías].

## Capturas

- [Captura del dashboard funcionando]
- [Captura de las pruebas unitarias]
- [Captura del diagrama de red una vez construido]
- [Captura de los controles de seguridad Linux una vez aplicados]

## Próximos pasos

1. Completar laboratorio Cisco Packet Tracer.
2. Desplegar VM Linux y hardening.
3. Integrar eventos con herramientas de monitorización.
4. Medir resultados y redactar conclusiones.

## Enlaces

- GitHub: [URL pendiente]
- LinkedIn: https://www.linkedin.com/in/alejandro-oliach
- CV: [URL pendiente]
