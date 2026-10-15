# Guía de hardening Linux (fase prevista)

**Estado: PENDIENTE.** Documentar cada acción y su evidencia una vez aplicada en una VM Debian/Ubuntu del laboratorio.

1. Instalar el sistema desde una ISO oficial y actualizar paquetes.
2. Crear un usuario no privilegiado; usar `sudo` solo cuando corresponda.
3. Configurar autenticación SSH por clave pública **y probarla en una segunda sesión antes de desactivar contraseña**.
4. Restringir SSH por firewall (UFW/nftables) a la VLAN de gestión; confirmar el acceso antes de habilitar reglas restrictivas.
5. Revisar servicios escuchando, desactivar los innecesarios y habilitar actualizaciones de seguridad.
6. Mantener sincronización horaria para correlacionar eventos.
7. Generar registros de prueba **solo en la VM propia** y exportar versiones anonimizadas para analizarlas.
8. Configurar y verificar una copia de seguridad de configuración, con prueba de restauración.
9. Documentar: versión del SO, servicio, cambio, objetivo, prueba, resultado y posible rollback.

**Evita** publicar ficheros `/etc/shadow`, claves SSH privadas, contraseñas, direcciones públicas reales o registros sin anonimizar.
