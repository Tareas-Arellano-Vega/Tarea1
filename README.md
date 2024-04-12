# Tarea1 (Intro Testing)
Github dedicado a tarea 1 enla cual se nos dio un requerimiento, para que nosotros construyamos el programa

## Tabla de Contenidos

1. [Requerimientos y Organización](#instalación)
2. [Uso](#uso)
3. [Contribución](#contribución)
4. [Licencia](#licencia)

## Requerimientos y Organización

El requerimiento especificado en la tarea 1 es que se pueda almacenar y gestionar contraseñas de forma **segura** en línea de comandos, la gestión debe tener las opciones para agregar, actualizar y eliminar contraseñas. Tambien debe haber una opción para generar contraseñas.

El requerimiento de seguridad de las contraseñas lo abarcamos de la siguiente manera:
1-El sistema guardará hará un hash md5, además de la respectiva encriptación de las contraseñas, para que asi no puedan ser accedidas de ninguna manera.
2-El sistema no permitira que otros perfiles puedan administrar las contraseñas de otros perfiles, esto implica todas las funcionalidades de la administración de estas.
3-El sistema de perfiles tambien requerira la contraseña propia del perfil para poder efectuar las funcionalidades pertenecientes a los perfiles, tales como: seleccionar un perfil, borrar un perfil y administrar contraseñas. (El sistema tambien aplicara un hash md5 y encriptación para estas contraseñas)
4- El perfil seleccionado puede administrar sus contraseñas, puede añadir contraseñas, en donde el sistema le pedira al usuario que ingresé: la web la que pertenece la contraseña, el usuario, una palabra clave y la contraseña del sitio, si la contraseña fue guardada exitosamente el sistema lo dirá en la línea de comandos al igual que si falla esta funcionalidad. Para la obtención de las contraseñas el sistema le pedirá al usuario que ingrese el nombre de la web que quiere ver su contraseña, y el sistema le entregara los datos guardados sobre ese sitio. Para la actualización de las cvontraseñas el sistema solicitará que ingrese los nuevos datos al usuario para actualizarlos. Para borrar contraseñas el sistema le pedira al usuario que ingrese el sitio del que quiere borrar la contraseña guardada., en caso de que ocurra con exito, el sistema lo reportara por la linea de comando y viceversa si es que falla.

Para asegurar los requerimientos del programa se realizarán pruebas de unidad, pruebas de integracíon, pruebas de sistema y revisión de código. Se realizarán pruebas de de manera individual, se preparará un conjunto y se ejecutarán de manera manual sobre el programa

## Organización

Uno se dedicará a realizar el código, mientras el otro se enfocará en las conexiones entre los programas de organización, tales como Jira, Github y Slack, además del propio testing del programa. La comunicación principal será vía Whatsapp

**Incluir evidencia del flujo de trabajo(aqui)**

## Problemas encontrados

1- En el programa se contruyó de menor a mayor ; es decir; se trabajo en base a un prototipo de administración de contraseñas en donde se creaba un archivo JSON en donde guardaban los datos de la contraseña sin encriptación, entonces a la hora de implementar la encriptación el arhcivo JSON marca que esta mal escrito, ya que las encriptarse no mantienen el formato JSON, pero el programa funciona muy bien igualmente, por lo que decidimos dejarlo como esta.

2- La conexión entre Github y Slack, no funciona del todo bien, debido a que no notifica los cambios que se realizan en otras branch que no sean la main, por loq ue slack no notifica los cambios que se realizan en repositorio, no lo solucionamos, ya que decidimos centrarnos en el programa y en el testing del mismo.


